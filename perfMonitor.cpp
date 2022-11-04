#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <asm/unistd.h>
#include <sys/mman.h>
#include <inttypes.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <errno.h>
#include <chrono>
#include <thread>
#include <future>
#include <fstream>
#include <vector>
#include <map>
#include <boost/algorithm/string/trim.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string.hpp>
using namespace std;

#define	OW_PORT	7778
#define	get_name(var)	#var

int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
vector<uint64_t> past_ns(num_cores);

// MB
float membw = 0;
// kB
float iobw = 0;

int sock_bind() {
	int con_sock = -1;
	struct sockaddr_in serv_addr;

	con_sock = socket(PF_INET, SOCK_STREAM, 0);
	if (con_sock == -1) {
		printf("[ERROR] socket creation error\n");
		exit(-1);
	}

	memset(&serv_addr, 0, sizeof(struct sockaddr_in));
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	serv_addr.sin_port = htons(OW_PORT);

	if (bind(con_sock, (struct sockaddr*) &serv_addr, sizeof(serv_addr)) == -1) {
		printf("[ERROR] bind error");
	}

	return con_sock;
}

int sock_bind_and_accept() {
	int con_sock = sock_bind();
	int acc_sock = -1;
	struct sockaddr_in client_addr;
	socklen_t client_addr_len = sizeof(struct sockaddr_in);

	if (listen(con_sock, 10) == -1) {
		printf("[ERROR] listen error");
	}

	if ((acc_sock = accept(con_sock, (struct sockaddr*) &client_addr, &client_addr_len)) == -1) {
		printf("[ERROR] accept error");
	}

	return acc_sock;
}

string build_msg(vector<double> mpki, vector<long> avgs, uint64_t cpu, uint64_t mem, double ipc, double mlp) {
	string res = "";
	res += to_string(ipc) + "@";
	res += to_string(mlp) + "@";

	for (double item : mpki) {
		res += to_string(item) + "@";
	}

	for (long item : avgs) {
		res += to_string(item) + "@";
	}

	res += to_string(cpu) + "@";
	res += to_string(mem) + "@";
	res += to_string(membw) + "@";
	res += to_string(iobw);
	
	return res;
}

void write_sock(int sock, string msg) {
	write(sock, msg.c_str(), msg.size());
}

int membw_mon(int interval) {
	double interval_ms = interval / 1000.0;
	string cmd = "perf stat -M DRAM_BW_Use sleep " + to_string(interval_ms) + " 2>&1";

	while (true) {
		FILE *p = popen(cmd.c_str(), "r");

		if (p == NULL) {
			printf("popen() failure\n");
			return -1;
		}

		char buf[4096];
		int cnt = 0;
		// auto start = chrono::system_clock::now();
		while (fgets(buf, 4096, p)) {
			string res = buf;
			if (cnt == 0) {
				membw = 0;
			}

			// 3: read bw, 4: write bw
			if (cnt == 3 | cnt == 4) {
				boost::algorithm::trim(res);
				vector<string> splitted;
				boost::algorithm::split(splitted, res, boost::is_any_of("\t "));

				membw += stof(splitted[0]);
			}
			cnt++;
		}
		// auto end = chrono::system_clock::now();
		// printf("membw: %lf\n", membw);
		// printf("membw duration: %ld ms\n", chrono::duration_cast<chrono::milliseconds>(end - start).count());
	}
	return 0;
}

int iobw_mon(int interval) {
	string cmd = "iostat -d";

	while (true) {
		FILE *p = popen(cmd.c_str(), "r");

		if (p == NULL) {
			printf("popen() failure\n");
			return -1;
		}

		char buf[4096];
		int cnt = 0;
		iobw = 0;
		while (fgets(buf, 4096, p)) {
			string res = buf;

			if (cnt > 2) {
				vector<string> splitted;
				boost::algorithm::split(splitted, res, boost::is_any_of("\t "));
				int data_cnt = 0;
				for (string spt : splitted) {
					if (spt.size() == 0) {
						continue;
					}

					if (data_cnt == 2 | data_cnt == 3) {
						iobw += stof(spt);
					}
					data_cnt++;
				}
			}

			cnt++;

		}
		this_thread::sleep_for(chrono::milliseconds(interval));
	}

	return 0;
}

uint64_t update_cpu_ns() {
	std::ifstream stream("/sys/fs/cgroup/cpu/cpuacct.usage_percpu");
	std::string reader;
	std::getline(stream, reader);
	uint64_t avg_cpu = 0;

	boost::trim_right(reader);
	std::vector<std::string> str_ns;
	std::vector<uint64_t> cur_ns;
	boost::algorithm::split(str_ns, reader, boost::is_any_of(" "));

	for (auto item : str_ns) {
		cur_ns.push_back(std::stoull(item));
	}

	for (int i = 0; i < num_cores; i++) {
		uint64_t tmp = cur_ns[i] - past_ns[i];
		avg_cpu += tmp;
	}
	past_ns = cur_ns;
	avg_cpu /= num_cores;

	stream.close();

	printf("avg_cpu: %lu\n", avg_cpu);
	return avg_cpu;
}

uint64_t read_mem_util() {
	std::ifstream stream("/proc/meminfo");
	std::string reader;
	uint64_t total, available, in_use;

	for (int i = 0; i < 3; i++) {
		std::getline(stream, reader);
		boost::erase_all(reader, " ");
		vector<string> tmp;
		boost::algorithm::split(tmp, reader, boost::is_any_of(":,kB"));
		
		if (tmp[0] == "MemTotal") {
			total = std::stoull(tmp[1]);
		}
		else if (tmp[0] == "MemAvailable") {
			available = std::stoull(tmp[1]);
		}
	}
	in_use = total - available;
	stream.close();

	printf("mem_util: %lu\n", in_use);
	return in_use;
}

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu,
		int group_fd, unsigned long flags) {
	int ret;
	ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
	return ret;
}

struct per_cpu_event {
	int *fd;	
	long long *count;
};

void accumulate_metrics(struct per_cpu_event *cpu, int num_events, uint64_t cpu_util, uint64_t mem_util) {
	vector<long long> total_per_event(num_events);
	vector<double> mpki;
	vector<long> avgs;
	int num_avail_cores = 0;

	for (int i = 0; i < num_cores; i++) {
		if (cpu[i].count[0] == 0) {
			continue;
		}
		else {
			num_avail_cores++;
		}
		
		for (int j = 0; j < num_events; j++) {
			total_per_event[j] += cpu[i].count[j];
		}
	}

	if (num_avail_cores == 0) {
		printf("There are no available cores!\n");
		return;
	}

	long total_inst = total_per_event[1];
	double ipc = double(total_inst) / double(total_per_event[0]);
	double mlp = double(total_per_event[13]) / double(total_per_event[14]);

	for (int i = 3; i < 7; i++) {
		avgs.push_back(total_per_event[i] / num_avail_cores);
	}

	double branch_mpki = double(total_per_event[2]) / double(total_inst);
	mpki.push_back(branch_mpki);
	for (int i = 7; i < 13; i++) {
		double tmp_mpki = double(total_per_event[i]) / double(total_inst);
		mpki.push_back(tmp_mpki);
	}

	build_msg(mpki, avgs, cpu_util, mem_util, ipc, mlp);

	printf("Number of available cores: %d\n", num_avail_cores);
	printf("==========\n");
	printf("IPC: %lf\n", ipc);
	printf("MLP: %lf\n", mlp);
	// printf("Cycles: %ld\n", avg_per_event[0]);
	// printf("Instructions: %ld\n", avg_per_event[1]);
	printf("Branch misses: %lf\n", mpki[0]);	// MPKI
	printf("CPU clock: %ld\n", avgs[0]);	// avg
	printf("Page faults: %ld\n", avgs[1]);	// avg
	printf("CPU migrations: %ld\n", avgs[2]);	// avg
	printf("Context switches: %ld\n", avgs[3]);	// avg
	printf("L1D read misses: %lf\n", mpki[1]);	// MPKI
	printf("L1I read misses: %lf\n", mpki[2]);	// MPKI
	printf("LLC read misses: %lf\n", mpki[3]);	// MPKI
	printf("DTLB read misses: %lf\n", mpki[4]);	// MPKI
	printf("ITLB read misses: %lf\n", mpki[5]);	// MPKI
	printf("l2_rqsts.all_demand_miss: %lf\n", mpki[6]);	// MPKI
	printf("==========\n");	

}

int perf_count_multicore(int interval, int sock) {

	struct perf_event_attr pe_def[] = {
		{ .type = PERF_TYPE_HARDWARE, .config = PERF_COUNT_HW_CPU_CYCLES },
		{ .type = PERF_TYPE_HARDWARE, .config = PERF_COUNT_HW_INSTRUCTIONS },
		{ .type = PERF_TYPE_HARDWARE, .config = PERF_COUNT_HW_BRANCH_MISSES },

		{ .type = PERF_TYPE_SOFTWARE, .config = PERF_COUNT_SW_CPU_CLOCK },
		{ .type = PERF_TYPE_SOFTWARE, .config = PERF_COUNT_SW_PAGE_FAULTS },
		{ .type = PERF_TYPE_SOFTWARE, .config = PERF_COUNT_SW_CPU_MIGRATIONS },
		{ .type = PERF_TYPE_SOFTWARE, .config = PERF_COUNT_SW_CONTEXT_SWITCHES },

		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_L1D) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_L1I) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_LL) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_DTLB) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_ITLB) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_MISS << 16) },

		{ .type = PERF_TYPE_RAW, .config = 0x2724 },	// l2_rqsts.all_demand_miss -> exclude prefetch miss
		{ .type = PERF_TYPE_RAW, .config = 0x148 },		// l1d_pend_miss.pending
		{ .type = PERF_TYPE_RAW, .config = 0x1000148 },	// l1d_pend_miss.pending_cycles
		/*
		{ .type = PERF_TYPE_RAW, .config = 0xc0},	// inst_retired.any
		{ .type = PERF_TYPE_RAW, .config = 0x8d1},	// mem_load_retired.l1_miss
		{ .type = PERF_TYPE_RAW, .config = 0x10d1},	// mem_load_retired.l2_miss
		{ .type = PERF_TYPE_RAW, .config = 0x20d1},	// mem_load_retired.l3_miss
		{ .type = PERF_TYPE_RAW, .config = 0x3f24},	// l2_rqsts.miss
		
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_L1D) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_LL) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_DTLB) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16) },
		{ .type = PERF_TYPE_HW_CACHE, .config = (PERF_COUNT_HW_CACHE_ITLB) | (PERF_COUNT_HW_CACHE_OP_READ << 8) | (PERF_COUNT_HW_CACHE_RESULT_ACCESS << 16) },
		*/
	};

	// long num_cores = 1;
	int num_events = sizeof(pe_def) / sizeof(struct perf_event_attr);

	struct perf_event_attr pe;
	struct per_cpu_event *cpu;
 
	cpu = (struct per_cpu_event *)calloc(num_cores, sizeof(struct per_cpu_event));
	for (int i = 0; i < num_cores; i++) {
		cpu[i].count = (long long *)calloc(num_events, sizeof(long long));
		cpu[i].fd = (int *)calloc(num_events, sizeof(int));
	}

	memset(&pe, 0, sizeof(struct perf_event_attr));
	pe.size = sizeof(struct perf_event_attr);
	pe.disabled = 1;
	pe.exclude_kernel = 1;
	pe.exclude_hv = 1;

	for (int i = 0; i < num_cores; i++) {
		for (int j = 0; j < num_events; j++) {
			pe.type = pe_def[j].type;
			pe.config = pe_def[j].config;
			cpu[i].fd[j] = perf_event_open(&pe, -1, i, -1, 0);

			if (cpu[i].fd[j] == -1) {
				printf("Error opening leader %llx, errno: %d\n", pe.config, errno);	
				// return -1;
			}
		}
	}

	printf("Start monitoring!\n");
	while(true) {

		for (int i = 0; i < num_cores; i++) {
			for (int j = 0; j < num_events; j++) {
				ioctl(cpu[i].fd[j], PERF_EVENT_IOC_RESET, 0);
				ioctl(cpu[i].fd[j], PERF_EVENT_IOC_ENABLE, 0);
			}
		}

		this_thread::sleep_for(chrono::milliseconds(interval));

		auto start = chrono::system_clock::now();
		for (int i = 0; i < num_cores; i++) {
			for (int j = 0; j < num_events; j++) {
				ioctl(cpu[i].fd[j], PERF_EVENT_IOC_DISABLE, 0);
				read(cpu[i].fd[j], &(cpu[i].count[j]), sizeof(cpu[i].count[j]));
			}
		}
		auto end = chrono::system_clock::now();
		uint64_t cpu_util = update_cpu_ns();
		uint64_t mem_util = read_mem_util();

		printf("read duration: %ld us\n", chrono::duration_cast<chrono::microseconds>(end - start).count());
		accumulate_metrics(cpu, num_events, cpu_util, mem_util);
	}

	for (int i = 0; i < num_cores; i++) {
		free(cpu[i].fd);
		free(cpu[i].count);
	}
	free(cpu);


	return 0;
}

int main() {
	// int sock = sock_bind_and_accept();
	int mon_interval = 100;	// ms

	thread perf(perf_count_multicore, mon_interval, -1);
	thread membw(membw_mon, mon_interval);
	thread iobw(iobw_mon, mon_interval);

	perf.join();
	membw.join();
	iobw.join();

	return 0;
}
