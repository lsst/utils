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

#ifndef LSST_UTILS_PACKAGING_H
#define LSST_UTILS_PACKAGING_H

#include <string>

namespace lsst {
namespace utils {

/*!
 * \brief return the root directory of a setup package
 *
 * \param[in] packageName  name of package (e.g. "utils")
 *
 * \throw lsst::pex::exceptions::NotFoundError if desired version can't be found
 */
std::string getPackageDir(std::string const& packageName);

}} // namespace lsst::utils

#endif
