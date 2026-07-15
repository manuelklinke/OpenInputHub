#include "spc_ctrlr.h"

#include <chrono>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace {

struct Options {
    bool help = false;
    bool timestamps = false;
    bool full_run = true;
    std::string single_call;
    int dev_idx = 0;
    int poll_count = 25;
};

void print_usage(const char* argv0) {
    std::cout
        << "Usage: " << argv0 << " [options]\n\n"
        << "Read-only SpaceControl SDK diagnostic tool.\n\n"
        << "Options:\n"
        << "  --help              Show this help text and exit\n"
        << "  --timestamps        Print wall-clock timestamps before SDK calls\n"
        << "  --single <call>     Run one device call only after connecting\n"
        << "                      Calls: devinfo, basic, advanced, fmwstate,\n"
        << "                             raw, lcd, leds, msg, std\n"
        << "  --dev <idx>         Device index for --single (default: 0)\n"
        << "  --poll-count <n>    Iterations for std polling (default: 25)\n";
}

bool parse_int(const std::string& value, int* out) {
    char* end = nullptr;
    long parsed = std::strtol(value.c_str(), &end, 10);
    if (end == value.c_str() || *end != '\0') {
        return false;
    }
    *out = static_cast<int>(parsed);
    return true;
}

bool parse_options(int argc, char** argv, Options* options) {
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--help" || arg == "-h") {
            options->help = true;
        } else if (arg == "--timestamps") {
            options->timestamps = true;
        } else if (arg == "--single") {
            if (i + 1 >= argc) {
                std::cerr << "--single requires a call name\n";
                return false;
            }
            options->full_run = false;
            options->single_call = argv[++i];
        } else if (arg == "--dev") {
            if (i + 1 >= argc || !parse_int(argv[++i], &options->dev_idx)) {
                std::cerr << "--dev requires an integer\n";
                return false;
            }
        } else if (arg == "--poll-count") {
            if (i + 1 >= argc || !parse_int(argv[++i], &options->poll_count)) {
                std::cerr << "--poll-count requires an integer\n";
                return false;
            }
        } else {
            std::cerr << "Unknown option: " << arg << "\n";
            return false;
        }
    }

    if (!options->single_call.empty()) {
        const std::vector<std::string> calls{
            "devinfo",
            "basic",
            "advanced",
            "fmwstate",
            "raw",
            "lcd",
            "leds",
            "msg",
            "std"};
        bool known = false;
        for (const std::string& call : calls) {
            if (options->single_call == call) {
                known = true;
                break;
            }
        }
        if (!known) {
            std::cerr << "Unknown --single call: " << options->single_call << "\n";
            return false;
        }
    }

    if (options->poll_count < 1) {
        std::cerr << "--poll-count must be at least 1\n";
        return false;
    }

    return true;
}

std::string timestamp() {
    using clock = std::chrono::system_clock;
    const auto now = clock::now();
    const auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(
                            now.time_since_epoch()) %
                        1000;
    const std::time_t seconds = clock::to_time_t(now);
    std::tm tm{};
    localtime_r(&seconds, &tm);

    std::ostringstream out;
    out << std::put_time(&tm, "%H:%M:%S") << '.'
        << std::setw(3) << std::setfill('0') << millis.count()
        << std::setfill(' ');
    return out.str();
}

void mark_call(const Options& options, const std::string& label) {
    if (options.timestamps) {
        std::cout << "[ts " << timestamp() << "] " << label << "\n";
    }
}

std::string status_text(ScStatus status) {
    char* text = scStatusToStr(status);
    if (text == nullptr) {
        return "unknown";
    }
    return text;
}

void print_status(const std::string& label, ScStatus status) {
    std::cout << std::left << std::setw(34) << label << " -> "
              << static_cast<int>(status) << " (" << status_text(status) << ")\n";
}

void print_daemon_param(const std::string& label, DaemonPar parameter) {
    int value = -1;
    ScStatus status = scGetDaemonPar(parameter, &value);
    print_status(label, status);
    if (status == SC_OK) {
        std::cout << "  value: " << value << "\n";
    }
}

std::string hex_dump(const unsigned char* data, int len) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (int i = 0; i < len; ++i) {
        if (i > 0) {
            out << ' ';
        }
        out << std::setw(2) << static_cast<unsigned int>(data[i]);
    }
    return out.str();
}

void print_device_info(int dev_idx) {
    ScDevInfo info{};
    ScStatus status = scGetDevInfo(dev_idx, &info);
    print_status("scGetDevInfo(" + std::to_string(dev_idx) + ")", status);
    if (status == SC_OK) {
        std::cout << "  id:          " << info.mId << "\n";
        std::cout << "  serial:      " << info.mSerialNo << "\n";
        std::cout << "  description: " << info.mDescrptn << "\n";
    }
}

void print_basic_settings(int dev_idx) {
    ScBasicSettings basic;
    ScStatus basic_status = scGetBasicSettings(dev_idx, &basic);
    print_status("scGetBasicSettings(" + std::to_string(dev_idx) + ")", basic_status);
    if (basic_status == SC_OK) {
        std::cout << "  dominant:        " << basic.mIsDom << "\n";
        std::cout << "  trans sens:      " << basic.mTraSens << "\n";
        std::cout << "  rot sens:        " << basic.mRotSens << "\n";
        std::cout << "  null radius:     " << basic.mNullRadius << "\n";
        std::cout << "  blue brightness: " << basic.mBrightnessBlue << "\n";
        std::cout << "  lcd brightness:  " << basic.mBrightnessDspl << "\n";
    }
}

void print_advanced_settings(int dev_idx) {
    ScAdvancedSettings advanced;
    ScStatus advanced_status = scGetAdvancedSettings(dev_idx, &advanced);
    print_status("scGetAdvancedSettings(" + std::to_string(dev_idx) + ")", advanced_status);
    if (advanced_status == SC_OK) {
        std::cout << "  axes enabled:    "
                  << "x=" << advanced.mIsX << ", y=" << advanced.mIsY
                  << ", z=" << advanced.mIsZ << ", a=" << advanced.mIsA
                  << ", b=" << advanced.mIsB << ", c=" << advanced.mIsC << "\n";
        std::cout << "  send delay:      " << advanced.mSendDelay << "\n";
        std::cout << "  average num:     " << advanced.mAverageNum << "\n";
        std::cout << "  dev lights:      " << advanced.mAreDevLights << "\n";
        std::cout << "  red brightness:  " << advanced.mBrightnessRed << "\n";
        std::cout << "  green brightness:" << advanced.mBrightnessGreen << "\n";
    }
}

void print_settings_reads(int dev_idx) {
    print_basic_settings(dev_idx);
    print_advanced_settings(dev_idx);
}

void print_firmware_update_state(int dev_idx) {
    int mcu_id = -1;
    int progress = -1;
    ScStatus firmware_status = scGetFmwUpdtState(dev_idx, &mcu_id, &progress);
    print_status("scGetFmwUpdtState(" + std::to_string(dev_idx) + ")", firmware_status);
    if (firmware_status == SC_OK) {
        std::cout << "  mcu id:   " << mcu_id << "\n";
        std::cout << "  progress: " << progress << "\n";
    }
}

void print_read_only_device_checks(int dev_idx) {
    print_firmware_update_state(dev_idx);

    unsigned char raw[RAW_DATA_LEN]{};
    ScStatus raw_status = scGetRawData(dev_idx, raw);
    print_status("scGetRawData(" + std::to_string(dev_idx) + ")", raw_status);
    if (raw_status == SC_OK) {
        std::cout << "  raw: " << hex_dump(raw, RAW_DATA_LEN) << "\n";
    }

    int lcd_brightness = -1;
    ScStatus lcd_status = scGetLcd(dev_idx, &lcd_brightness);
    print_status("scGetLcd(" + std::to_string(dev_idx) + ")", lcd_status);
    if (lcd_status == SC_OK) {
        std::cout << "  lcd brightness: " << lcd_brightness << "\n";
    }

    char leds[LED_NUM]{};
    ScStatus leds_status = scGetLedsEx(dev_idx, leds);
    print_status("scGetLedsEx(" + std::to_string(dev_idx) + ")", leds_status);
    if (leds_status == SC_OK) {
        std::cout << "  leds:";
        for (int i = 0; i < LED_NUM; ++i) {
            std::cout << ' ' << static_cast<int>(leds[i]);
        }
        std::cout << "\n";
    }

    char msg[MAX_STR_LEN]{};
    ScStatus msg_status = scReadMsg(dev_idx, msg);
    print_status("scReadMsg(" + std::to_string(dev_idx) + ")", msg_status);
    if (msg_status == SC_OK) {
        std::cout << "  msg: " << msg << "\n";
    }
}

void poll_standard_data(int dev_idx, int iterations) {
    std::cout << "\nStandard data polling\n";
    for (int i = 0; i < iterations; ++i) {
        short x = 0;
        short y = 0;
        short z = 0;
        short a = 0;
        short b = 0;
        short c = 0;
        int tra_lmh = 0;
        int rot_lmh = 0;
        int event = 0;
        long tv_sec = 0;
        long tv_usec = 0;

        ScStatus status = scFetchStdData(
            dev_idx,
            &x,
            &y,
            &z,
            &a,
            &b,
            &c,
            &tra_lmh,
            &rot_lmh,
            &event,
            &tv_sec,
            &tv_usec);

        std::cout << "  [" << std::setw(2) << i << "] "
                  << static_cast<int>(status) << " (" << status_text(status) << ")"
                  << " x=" << x
                  << " y=" << y
                  << " z=" << z
                  << " a=" << a
                  << " b=" << b
                  << " c=" << c
                  << " tra_lmh=" << tra_lmh
                  << " rot_lmh=" << rot_lmh
                  << " event=" << event
                  << " time=" << tv_sec << "." << std::setw(6) << std::setfill('0') << tv_usec
                  << std::setfill(' ') << "\n";

        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
}

void run_single_call(const Options& options) {
    const int dev_idx = options.dev_idx;

    if (options.single_call == "devinfo") {
        mark_call(options, "before scGetDevInfo(" + std::to_string(dev_idx) + ")");
        print_device_info(dev_idx);
        return;
    }

    if (options.single_call == "basic") {
        mark_call(options, "before scGetBasicSettings(" + std::to_string(dev_idx) + ")");
        print_basic_settings(dev_idx);
        return;
    }

    if (options.single_call == "advanced") {
        mark_call(options, "before scGetAdvancedSettings(" + std::to_string(dev_idx) + ")");
        print_advanced_settings(dev_idx);
        return;
    }

    if (options.single_call == "fmwstate") {
        mark_call(options, "before scGetFmwUpdtState(" + std::to_string(dev_idx) + ")");
        print_firmware_update_state(dev_idx);
        return;
    }

    if (options.single_call == "raw") {
        unsigned char raw[RAW_DATA_LEN]{};
        mark_call(options, "before scGetRawData(" + std::to_string(dev_idx) + ")");
        ScStatus status = scGetRawData(dev_idx, raw);
        print_status("scGetRawData(" + std::to_string(dev_idx) + ")", status);
        if (status == SC_OK) {
            std::cout << "  raw: " << hex_dump(raw, RAW_DATA_LEN) << "\n";
        }
        return;
    }

    if (options.single_call == "lcd") {
        int lcd_brightness = -1;
        mark_call(options, "before scGetLcd(" + std::to_string(dev_idx) + ")");
        ScStatus status = scGetLcd(dev_idx, &lcd_brightness);
        print_status("scGetLcd(" + std::to_string(dev_idx) + ")", status);
        if (status == SC_OK) {
            std::cout << "  lcd brightness: " << lcd_brightness << "\n";
        }
        return;
    }

    if (options.single_call == "leds") {
        char leds[LED_NUM]{};
        mark_call(options, "before scGetLedsEx(" + std::to_string(dev_idx) + ")");
        ScStatus status = scGetLedsEx(dev_idx, leds);
        print_status("scGetLedsEx(" + std::to_string(dev_idx) + ")", status);
        if (status == SC_OK) {
            std::cout << "  leds:";
            for (int i = 0; i < LED_NUM; ++i) {
                std::cout << ' ' << static_cast<int>(leds[i]);
            }
            std::cout << "\n";
        }
        return;
    }

    if (options.single_call == "msg") {
        char msg[MAX_STR_LEN]{};
        mark_call(options, "before scReadMsg(" + std::to_string(dev_idx) + ")");
        ScStatus status = scReadMsg(dev_idx, msg);
        print_status("scReadMsg(" + std::to_string(dev_idx) + ")", status);
        if (status == SC_OK) {
            std::cout << "  msg: " << msg << "\n";
        }
        return;
    }

    if (options.single_call == "std") {
        mark_call(options, "before scFetchStdData polling");
        poll_standard_data(dev_idx, options.poll_count);
    }
}

}  // namespace

int main(int argc, char** argv) {
    Options options;
    if (!parse_options(argc, argv, &options)) {
        print_usage(argv[0]);
        return 2;
    }

    if (options.help) {
        print_usage(argv[0]);
        return 0;
    }

    std::cout << "SpaceControl SDK diagnostic tool\n";
    std::cout << "Mode: read-only, no reset/write/firmware commands\n\n";

    mark_call(options, "before scConnect2(always receive)");
    ScStatus connect_status = scConnect2(true, nullptr);
    print_status("scConnect2(always receive)", connect_status);
    if (connect_status != SC_OK) {
        return 1;
    }

    if (!options.full_run) {
        run_single_call(options);
        ScStatus disconnect_status = scDisconnect();
        print_status("\nscDisconnect", disconnect_status);
        return disconnect_status == SC_OK ? 0 : 2;
    }

    mark_call(options, "before scGetDmnVrsn");
    char daemon_version[MAX_VERSION_LEN]{};
    char daemon_path[MAX_FILENAME_LEN]{};
    ScStatus daemon_status = scGetDmnVrsn(daemon_version, daemon_path);
    print_status("scGetDmnVrsn", daemon_status);
    if (daemon_status == SC_OK) {
        std::cout << "  version: " << daemon_version << "\n";
        std::cout << "  path:    " << daemon_path << "\n";
    }

    int dev_num = -1;
    int used_dev_num = -1;
    int max_dev_idx = -1;
    mark_call(options, "before scGetDevNum");
    ScStatus dev_num_status = scGetDevNum(&dev_num, &used_dev_num, &max_dev_idx);
    print_status("scGetDevNum", dev_num_status);
    if (dev_num_status == SC_OK) {
        std::cout << "  dev num:      " << dev_num << "\n";
        std::cout << "  used dev num: " << used_dev_num << "\n";
        std::cout << "  max dev idx:  " << max_dev_idx << "\n";
    }

    print_daemon_param("scGetDaemonPar(BAUD)", BAUD);
    print_daemon_param("scGetDaemonPar(SEND_DELAY)", SEND_DELAY);
    print_daemon_param("scGetDaemonPar(SEND_MODE)", SEND_MODE);
    print_daemon_param("scGetDaemonPar(DEVICE_TIMEOUT)", DEVICE_TIMEOUT);

    if (dev_num_status == SC_OK && max_dev_idx >= 0) {
        int upper = max_dev_idx;
        if (upper >= MAX_DEV_NUM) {
            upper = MAX_DEV_NUM - 1;
        }
        for (int dev_idx = 0; dev_idx <= upper; ++dev_idx) {
            std::cout << "\nDevice index " << dev_idx << "\n";
            print_device_info(dev_idx);
            if (dev_idx == 0) {
                print_settings_reads(dev_idx);
                print_read_only_device_checks(dev_idx);
                poll_standard_data(dev_idx, 25);
            }
        }
    }

    ScStatus disconnect_status = scDisconnect();
    print_status("\nscDisconnect", disconnect_status);
    return disconnect_status == SC_OK ? 0 : 2;
}
