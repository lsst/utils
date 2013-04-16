/*------------------------------------------------------------------------------

   HXA7241 General library.
   Harrison Ainsworth / HXA7241 : 2004-2011

   http://www.hxa.name/

------------------------------------------------------------------------------*/




#include <cmath>
#include <float.h>
#include <ostream>
#include <iomanip>

#include <cstdlib>
#include <exception>
#include <iostream>

#include "lsst/utils/PowFast.h"

// constants -------------------------------------------------------------------
namespace
{

const char BANNER_MESSAGE[] =
   "\n  PowFast tester  :  HXA7241\n"
   "  http://www.hxa.name/articles/content/"
   "fast-pow-adjustable_hxa7241_2007.html\n\n";
const char EXCEPTION_PREFIX[]   = "*** execution failed:  ";
const char EXCEPTION_ABSTRACT[] = "no annotation for cause";

}

/************************************************************************************************************/

typedef  unsigned int  udword;
typedef  int           dword;



namespace
{

/**
 * rand [0,1) (may be coarsely quantized).
 */
float randFloat()
{
   return static_cast<float>(static_cast<udword>(::rand())) /
      static_cast<float>(static_cast<udword>(RAND_MAX) + 1);
}

}

bool test_PowFast
(
   std::ostream* pOut,
   const bool    isVerbose,
   const dword   seed
)
{
   bool isOk = true;

   if( pOut ) *pOut << "[ test_PowFast ]\n\n";

   if( pOut )
   {
      pOut->setf( std::ios_base::scientific, std::ios_base::floatfield );
      pOut->precision( 6 );
   }


   ::srand( static_cast<unsigned>(seed) );

   /// adjustable
   const lsst::utils::PowFast& powFastAdj = lsst::utils::getPowFast<11>();
   
   const dword J_COUNT = 1000;

   float sumDifE = 0.0f;
   float maxDifE = static_cast<float>(FLT_MIN);

   const dword E_START = -86;
   const dword E_END   = +88;
   for( dword i = E_START;  i < E_END;  ++i )
   {
       for( dword j = 0;  j < J_COUNT;  ++j )
       {
           const float number = static_cast<float>(i) + randFloat();

           const float pe    = ::powf( 2.71828182845905f, number );
           const float pef   = powFastAdj.exp( number );
           const float peDif = ::fabsf( pef - pe ) / pe;
           sumDifE += peDif;
           maxDifE = (maxDifE >= peDif) ? maxDifE : peDif;

           if( (0 == j) && pOut && isVerbose )
           {
               *pOut << std::showpos << std::fixed << std::setw(10) << number <<
                   std::scientific << std::noshowpos;
               *pOut << "  E " << pef << " " << peDif << "\n";
           }
       }
   }
   if( pOut && isVerbose ) *pOut << "\n";

   float sumDifT = 0.0f;
   float maxDifT = static_cast<float>(FLT_MIN);

   const dword T_START = -36;
   const dword T_END   = +38;
   for( dword i = T_START;  i < T_END;  ++i )
   {
       for( dword j = 0;  j < J_COUNT;  ++j )
       {
           const float number = static_cast<float>(i) + randFloat();

           const float pt    = ::powf( 10.0f, number );
           const float ptf   = powFastAdj.ten( number );
           const float ptDif = ::fabsf( ptf - pt ) / pt;
           sumDifT += ptDif;
           maxDifT = (maxDifT >= ptDif) ? maxDifT : ptDif;

           if( (0 == j) && pOut && isVerbose )
           {
               *pOut << std::showpos << std::fixed << std::setw(10) << number <<
                   std::scientific << std::noshowpos;
               *pOut << "  T " << ptf << " " << ptDif << "\n";
           }
       }
   }
   if( pOut && isVerbose ) *pOut << "\n";

   const float meanDifE = sumDifE / (static_cast<float>(E_END - E_START) *
                                     static_cast<float>(J_COUNT));
   const float meanDifT = sumDifT / (static_cast<float>(T_END - T_START) *
                                     static_cast<float>(J_COUNT));

   if( pOut && isVerbose ) *pOut << "precision: " << powFastAdj.getPrecision() <<  "\n";
   if( pOut && isVerbose ) *pOut << "mean diff,  E: " << meanDifE << "  10: " << meanDifT << "\n";
   if( pOut && isVerbose ) *pOut << "max  diff,  E: " << maxDifE  << "  10: " << maxDifT  << "\n";
   if( pOut && isVerbose ) *pOut << "\n";

   bool isOk_ = (meanDifE < 0.0001f) & (meanDifT < 0.0001f) &
       (maxDifE < 0.0002f) & (maxDifT < 0.0002f);

   if( pOut ) *pOut << "adjustable : " <<
                  (isOk_ ? "--- succeeded" : "*** failed") << "\n\n";

   isOk &= isOk_;

   if( pOut ) *pOut << (isOk ? "--- successfully" : "*** failurefully") <<
      " completed " << "\n\n";

   if( pOut ) pOut->flush();


   return isOk;
}


/************************************************************************************************************/
/// entry point ////////////////////////////////////////////////////////////////
int main
(
   int   ,//argc,
   char* []//argv[]
)
{
   int returnValue = EXIT_FAILURE;

   // catch everything
   try
   {
      std::cout << BANNER_MESSAGE;

      const bool isOk = test_PowFast( &std::cout, true, 0 );

      returnValue = isOk ? EXIT_SUCCESS : EXIT_FAILURE;
   }
   // print exception message
   catch( const std::exception& e )
   {
      std::cout << '\n' << EXCEPTION_PREFIX << e.what() << '\n';
   }
   catch( const char*const pExceptionString )
   {
      std::cout << '\n' << EXCEPTION_PREFIX << pExceptionString << '\n';
   }
   catch( ... )
   {
      std::cout << '\n' << EXCEPTION_PREFIX << EXCEPTION_ABSTRACT << '\n';
   }

   try
   {
      std::cout.flush();
   }
   catch( ... )
   {
      // suppress exceptions
   }

   return returnValue;
}
