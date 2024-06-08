/* BEGIN_LEGAL 

Copyright (c) 2022 Intel Corporation

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
  
END_LEGAL */
/// @file xed-operand-element-type-enum.h

// This file was automatically generated.
// Do not edit this file.

#if !defined(XED_OPERAND_ELEMENT_TYPE_ENUM_H)
# define XED_OPERAND_ELEMENT_TYPE_ENUM_H
#include "xed-common-hdrs.h"
#define XED_OPERAND_ELEMENT_TYPE_INVALID_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_UINT_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_INT_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_SINGLE_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_DOUBLE_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_LONGDOUBLE_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_LONGBCD_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_STRUCT_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_VARIABLE_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_FLOAT16_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_BFLOAT16_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_INT8_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_UINT8_DEFINED 1
#define XED_OPERAND_ELEMENT_TYPE_LAST_DEFINED 1
typedef enum {
  XED_OPERAND_ELEMENT_TYPE_INVALID,
  XED_OPERAND_ELEMENT_TYPE_UINT, ///< Unsigned integer
  XED_OPERAND_ELEMENT_TYPE_INT, ///< Signed integer
  XED_OPERAND_ELEMENT_TYPE_SINGLE, ///< 32b FP single precision
  XED_OPERAND_ELEMENT_TYPE_DOUBLE, ///< 64b FP double precision
  XED_OPERAND_ELEMENT_TYPE_LONGDOUBLE, ///< 80b FP x87
  XED_OPERAND_ELEMENT_TYPE_LONGBCD, ///< 80b decimal BCD
  XED_OPERAND_ELEMENT_TYPE_STRUCT, ///< a structure of various fields
  XED_OPERAND_ELEMENT_TYPE_VARIABLE, ///< depends on other fields in the instruction
  XED_OPERAND_ELEMENT_TYPE_FLOAT16, ///< 16b floating point
  XED_OPERAND_ELEMENT_TYPE_BFLOAT16, ///< bfloat16 floating point
  XED_OPERAND_ELEMENT_TYPE_INT8, ///< 8 bit integer
  XED_OPERAND_ELEMENT_TYPE_UINT8, ///< 8 bit unsigned integer
  XED_OPERAND_ELEMENT_TYPE_LAST
} xed_operand_element_type_enum_t;

/// This converts strings to #xed_operand_element_type_enum_t types.
/// @param s A C-string.
/// @return #xed_operand_element_type_enum_t
/// @ingroup ENUM
XED_DLL_EXPORT xed_operand_element_type_enum_t str2xed_operand_element_type_enum_t(const char* s);
/// This converts strings to #xed_operand_element_type_enum_t types.
/// @param p An enumeration element of type xed_operand_element_type_enum_t.
/// @return string
/// @ingroup ENUM
XED_DLL_EXPORT const char* xed_operand_element_type_enum_t2str(const xed_operand_element_type_enum_t p);

/// Returns the last element of the enumeration
/// @return xed_operand_element_type_enum_t The last element of the enumeration.
/// @ingroup ENUM
XED_DLL_EXPORT xed_operand_element_type_enum_t xed_operand_element_type_enum_t_last(void);
#endif
