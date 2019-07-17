#ifndef HELLO_H
#define HELLO_H

#ifdef WIN32
#	if defined(HELLO_STATIC)
#		define HELLO_API 
#	elif defined(HELLO_EXPORTS)
#		define HELLO_API __declspec(dllexport)
#	else
#		define HELLO_API __declspec(dllimport)
#	endif
#else
#	define HELLO_API 
#endif

extern HELLO_API void hello();

#endif