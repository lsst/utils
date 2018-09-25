// -*- lsst-c++ -*-

/*
 * LSST Data Management System
 * Copyright 2008-2017  AURA/LSST.
 *
 * This product includes software developed by the
 * LSST Project (http://www.lsst.org/).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the LSST License Statement and
 * the GNU General Public License along with this program.  If not,
 * see <https://www.lsstcorp.org/LegalNotices/>.
 */

#if defined(LSST_UTILS_BACKTRACE_ENABLE) && (defined(__clang__) || defined(__GNUC__))

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <csignal>

#include <cxxabi.h>
#include <execinfo.h>

#include <regex>

#include "lsst/utils/Backtrace.h"

namespace lsst {
namespace utils {

namespace {

/// Maximum number of frames in the backtrace
static constexpr size_t MAX_FRAMES = 128;
/// Estimated number of characters in name
static constexpr size_t NAME_SIZE_ESTIMATE = 1024;

/**
 * Print symbol list entry to stderr, demangling the name if possible
 *
 * @param[in] input entry produced by backtrace_symbol
 * @param[out] buffer allocated with malloc for output of the demangled name
 *               if the name does not fit the bufferSize is increased with realloc
 *               the user is responsible for freeing the buffer
 * @param[in,out] bufferSize size of the name buffer (increased if needed)
 *
 * @return buffer (possibly reallocated) buffer for demangled name,
 *                caller should always free this.
 */
char *demangleAndPrint(char *input, char *buffer, size_t *bufferSize) noexcept {
    int status = 1;

    try {
        std::cmatch matches;
        std::regex rgx(
                "(.*[\\s|\\(])"  // before
                "(_\\w+)"        // mangled name
                "(.*\\+.*)"      // after
                );

        if (std::regex_match(input, matches, rgx)) {
            buffer = abi::__cxa_demangle(matches.str(2).c_str(), buffer, bufferSize, &status);
            fprintf(stderr, "%s%s%s\n", matches.str(1).c_str(), buffer, matches.str(3).c_str());
        }
    } catch(const std::regex_error &e) {
        fprintf(stderr, "[demangleAndPrint] %s\n", e.what());
        status = 1;
    } catch(const std::runtime_error &e) {
        fprintf(stderr, "[demangleAndPrint] %s\n", e.what());
        status = 1;
    } catch(const std::exception &e) {
        fprintf(stderr, "[demangleAndPrint] %s\n", e.what());
        status = 1;
    } catch(...) {
        fprintf(stderr, "[demangleAndPrint] unknown error occurred in demangling\n");
        status = 1;
    }

    if (status != 0) {
        // no name found to demangle or name demangling failed
        fprintf(stderr, "%s\n", input);
    }
    return buffer;
}

/**
 * Restore default signal handler and re-raise.
 *
 * This prevents breaking the debugger.
 *
 * @param[in] signum signal number to raise.
 */
void raiseWithDefaultHandler(int signum) noexcept {
    signal(signum, SIG_DFL);
    raise(signum);
}

/**
 * Handle signal.
 *
 * @param[in] signum signal number to handle.
 */
void signalHandler(int signum) noexcept {
    fprintf(stderr, "Caught signal %d, backtrace follows:\n", signum);

    // retrieve current stack addresses
    void *addressList[MAX_FRAMES + 1];
    size_t addressLength = backtrace(addressList, MAX_FRAMES);
    if (addressLength == 0) {
        fprintf(stderr, "  \n");
        return;
    }

    // translate the addresses into an array of strings
    // that describe the addresses symbolically.
    // return value symbolList is malloc'ed and must be free'd
    char **symbolList = backtrace_symbols(addressList, addressLength);
    if (symbolList == NULL) {
        fprintf(stderr, "[backtrace_symbols] cannot dump trace, probably out of memory\n");
        raiseWithDefaultHandler(signum);
    }

    // allocate storage for demangled name
    // this will be reallocated by abi::__cxa_demangle in demangleAndPrint
    // if storage is insufficient, but if it is sufficient
    // this reduces the number of allocations
    size_t nameSize = NAME_SIZE_ESTIMATE;
    char *name = (char *)malloc(nameSize * sizeof(char));
    if (name == NULL) {
        fprintf(stderr, "[malloc] cannot dump trace, probably out of memory\n");
        raiseWithDefaultHandler(signum);
    }

    for (size_t i = 0; i < addressLength; ++i) {
        if (char *buffer = demangleAndPrint(symbolList[i], name, &nameSize)) {
            // buffer may have been realloc'ed
            name = buffer;
        }
    }

    free(name);
    free(symbolList);
    raiseWithDefaultHandler(signum);
}

}  // namespace

Backtrace::Backtrace() noexcept : enabled(true) {
    // Register abort handlers
    signal(SIGABRT, signalHandler);
    signal(SIGSEGV, signalHandler);
    signal(SIGILL, signalHandler);
    signal(SIGFPE, signalHandler);
}

}  // namespace utils
}  // namespace lsst

#else

#include "lsst/utils/Backtrace.h"

namespace lsst {
namespace utils {

Backtrace::Backtrace() noexcept : enabled(false) {}

}  // namespace utils
}  // namespace lsst

#endif
