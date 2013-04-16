/**
\file

Harrison Ainsworth / HXA7241 : 2004-2011.

   http://www.hxa.name/

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.
* The name of the author may not be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
OF SUCH DAMAGE.

*/

#include <cmath>

#include "lsst/utils/PowFast.h"

// implementation -------------------------------------------------------------

/**
 * Following the bit-twiddling idea in:
 *
 * 'A Fast, Compact Approximation of the Exponential Function'
 * Technical Report IDSIA-07-98
 * Nicol N. Schraudolph;
 * IDSIA,
 * 1998-06-24.
 *
 * [Rewritten for floats by HXA7241, 2007.]
 *
 * and the adjustable-lookup idea in:
 *
 * 'Revisiting a basic function on current CPUs: A fast logarithm implementation
 * with adjustable accuracy'
 * Technical Report ICSI TR-07-002;
 * Oriol Vinyals, Gerald Friedland, Nikki Mirghafori;
 * ICSI,
 * 2007-06-21.
 *
 * [Improved (doubled accuracy) and rewritten by HXA7241, 2007.]
 */

namespace lsst { namespace utils {

namespace {

const float _2p23 = 8388608.0f;


/*
 * Initialize powFast lookup table.
 *
 * @param pTable     length must be 2 ^ precision
 * @param precision  number of mantissa bits used, >= 0 and <= 18
 */
void powFastSetTable(
                     unsigned int* const pTable,
                     const unsigned int  precision
                    )
{
   // step along table elements and x-axis positions
   float zeroToOne = 1.0f / (static_cast<float>(1 << precision) * 2.0f);
   for( int i = 0;  i < (1 << precision);  ++i )
   {
      // make y-axis value for table element
      const float f = (::powf( 2.0f, zeroToOne ) - 1.0f) * _2p23;
      pTable[i] = static_cast<unsigned int>( f < _2p23 ? f : (_2p23 - 1.0f) );

      zeroToOne += 1.0f / static_cast<float>(1 << precision);
   }
}


/**
 * Get pow (fast!).
 *
 * @param val        power to raise radix to
 * @param ilog2      one over log, to required radix, of two
 * @param pTable     length must be 2 ^ precision
 * @param precision  number of mantissa bits used, >= 0 and <= 18
 */
inline
float powFastLookup
(
   const float         val,
   const float         ilog2,
   unsigned int* const pTable,
   const unsigned int  precision
)
{
   // build float bits
   const int i = static_cast<int>( (val * (_2p23 * ilog2)) + (127.0f * _2p23) );

   // replace mantissa with lookup
   const int it = (i & 0xFF800000) | pTable[(i & 0x7FFFFF) >> (23 - precision)];

   // convert bits to float
   union { int i; float f; } pun;
   return pun.i = it,  pun.f;
}

}

// wrapper class --------------------------------------------------------------

PowFast::PowFast
(
   const unsigned int precision
)
 : precision_m( precision <= 18u ? precision : 18u )
 , pTable_m   ( new unsigned int[ 1 << precision_m ] )
{
   powFastSetTable( pTable_m, precision_m );
}


PowFast::~PowFast()
{
   delete[] pTable_m;
}


float PowFast::two
(
   const float f
) const
{
   return powFastLookup( f, 1.0f, pTable_m, precision_m );
}


float PowFast::exp
(
   const float f
) const
{
   return powFastLookup( f, 1.44269504088896f, pTable_m, precision_m );
}


float PowFast::ten
(
   const float f
) const
{
   return powFastLookup( f, 3.32192809488736f, pTable_m, precision_m );
}


float PowFast::r
(
   const float logr,
   const float f
) const
{
   return powFastLookup( f, (logr * 1.44269504088896f), pTable_m, precision_m );
}


unsigned int PowFast::getPrecision() const
{
   return precision_m;
}
}}
