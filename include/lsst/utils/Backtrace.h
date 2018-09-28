// -*- lsst-c++ -*-
/*
 * LSST Data Management System
 * See COPYRIGHT file at the top of the source tree.
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
 * see <http://www.lsstcorp.org/LegalNotices/>.
 */


#ifndef LSST_UTILS_BACKTRACE_H
#define LSST_UTILS_BACKTRACE_H

namespace lsst {
namespace utils {

/**
 *  Singleton, enables automatic backtraces on the following signals:
 *
 *  - SIGABRT
 *  - SIGSEGV
 *  - SIGILL
 *  - SIGFPE
 *
 *  @note Uses low level malloc and fprintf since higher level constructs
 *  may not be available when a signal is received.
 */
class Backtrace final {
public:
    // No copying and moving
    Backtrace(Backtrace const&) = delete;
    Backtrace(Backtrace&&) = delete;
    Backtrace& operator=(Backtrace const&) = delete;
    Backtrace& operator=(Backtrace&&) = delete;

    /// Get a reference to the singleton
    static Backtrace& get() noexcept {
        static Backtrace st;
        return st;
    }

    bool const isEnabled() const noexcept { return enabled; }

private:
    Backtrace() noexcept;

    bool const enabled;
};

}  // namespace utils
}  // namespace lsst

#endif
