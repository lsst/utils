// -*- LSST-C++ -*-
/*
 * This file is part of utils.
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
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
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/**
 * @file
 * @brief Utilities for converting between flux and magnitude in C++.
 *
 * Use `astropy.units` `ABmag` and `nJy` for converstions in python:
 * @code{.python}
 *   import astropy.units as u
 *   mag = (flux*u.nJy).to_value(u.ABmag)
 *   flux = (mag*u.ABmag).to_value(u.nJy)
 * @endcode
 */

#ifndef LSST_UTILS_MAGNITUDE_H
#define LSST_UTILS_MAGNITUDE_H

#include <cmath>

namespace lsst {
namespace utils {

/// The Oke & Gunn (1983) AB magnitude reference flux, in nJy (often approximated as 3631.0).
const double referenceFlux = 1e23 * pow(10, (48.6 / -2.5)) * 1e9;

/// Convert a flux in nanojansky to AB magnitude.
double nanojanskyToABMagnitude(double flux);

/// Convert an AB magnitude to a flux in nanojansky.
double ABMagnitudeToNanojansky(double magnitude);

}  // namespace utils
}  // namespace lsst

#endif  // LSST_UTILS_MAGNITUDE_H
