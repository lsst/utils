/*------------------------------------------------------------------------------

   HXA7241 General library.
   Harrison Ainsworth / HXA7241 : 2004-2011

   http://www.hxa.name/

------------------------------------------------------------------------------*/


#ifndef LSST_UTILS_POWFAST_H
#define LSST_UTILS_POWFAST_H

namespace lsst { namespace utils {


/**
 * \defgroup PowFast lsst::utils::PowFast
 * @{
 *
 * \brief Fast approximation to pow and exp, with adjustable precision
 *
 * The PowFast class has member functions to calculate pow and exp with the
 * specified precision, and getPowFast may be used to return a singleton PowFast object e.g.
 * \code
 * #include "lsst/utils/PowFast.h"
 *
 * auto pf = lsst::utils::getPowFast<11>();
 *
 * float x = 1;
 * std::cout << std::exp(x) << " " << pf::exp(x) << std::endl;
 * \endcode
 *
 * \note
 * Please do not use these routines without profiling and a code review!  There are places where it's a good
 * tradeoff, but the average casual user of exp() should stick to std::exp()
 *
 * Precision can be 0 to 18.<br/>
 * Storage is 4*(2^precision) bytes -- 4B to 1MB<br/>
 * For precision 11: mean error < 0.01%, max error < 0.02%, storage 8KB.
 */
class PowFast;
template<int> const PowFast& getPowFast(); // forward declaration

class PowFast {
public:
    template<int> friend const PowFast& getPowFast();


    /// Evaluate 2^x . (x must be in (-125, 128))
    float two(float x                   ///< exponent
             ) const;
    
    /// Evaluate exp(x). (x must be in (-87.3ish, 88.7ish))
    float exp(float x                   ///< exponent
           ) const;

    /// Evaluate  10^x. (x must be in (-37.9ish, 38.5ish))
    float ten(float x                   ///< exponent
             ) const;

    /**
     * \brief Evaluate r^x
     */
    float r(float logr,                 ///< log_e(r)
            float x                     ///< desired exponent (beware under/over-flow)
           )const;

    /**
     * \brief Return this PowFast's precision
     */
    unsigned int getPrecision() const;

private:
    explicit PowFast( unsigned int precision = 11 ///< Desired precision
                    );
    ~PowFast();
    PowFast(const PowFast&);
    PowFast& operator=(const PowFast&);

    unsigned int  precision_m;
    unsigned int* pTable_m;
};

/**
 * \brief return a singleton PowFast with the specified precision in its lookup tables
 */
template<int precision /* = 11 */>		// Default values for functions are new in C++11
const PowFast& getPowFast()
{
   static const PowFast k(precision);
   return k;
}
/**
 * @}
 */

}}
#endif
