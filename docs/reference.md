# Reference Manual

* [Functions](#functions)
  * [ignore_extra_fields](#ignore-extra-fields)
  * [optional](#optional)
  * [required](#required)
  * [validate](#validate)
* [Classes](#classes)
  * [Message](#message)
  * [SchemaError](#schema-error)
* [Type validators](#type-validators)
  * [bool](#bool)
  * [custom](#custom)
  * [int](#int)
  * [list](#list)
  * [number](#number)
  * [object](#object)
  * [string](#string)
* [Validaton messages](#validation-messages)
  * [invalid_option](#invalid_option)
  * [invalid_type](#invalid_type)
  * [no_match](#no_match)
  * [null_value](#null_value)
  * [number_too_large](#number_too_large)
  * [number_too_small](#number_too_small)
  * [too_few_elements](#too_few_elements)
  * [too_many_elements](#too_many_elements)

## Functions

### ignore_extra_fields

You use `ignore_extra_fields()` inside a [schema definition](user-guide.md#writing-a-schema) to tell the validator to accept any field that you didn't explicitly define using [`optional()`](#optional) or [`required()`](#required). By default, the validator will report any such field, so `ignore_extra_fields()` will turn reporting extra fields off.

`ignore_extra_fields()` has no parameters and no return value.

### optional

You use `optional()` inside a [schema definition](user-guide.md#writing-a-schema) to indicate that a field is allowed to be in a document, but it's fine if the field is missing.

`optional()` has no return value.

Parameter | Description
----------|------------
`field`     | Required. The name of the field you want to validate. You can specify [nested fields](user-guide.md#nested-fields) using the `.` separator, e.g. `author.last_name`. You can specify [list elements](user-guide.md#lists) using the `[]` suffix, e.g. `genres[]`.
`type`      | Optional. The [type](#type-validators) the field should have.

Depending on the [type](#type-validators) you specify, you can pass extra named parameters to `optional()`. For example, if a field is of type `string`, you can pass a `regex` parameter.

### required

You use `required()` inside a [schema definition](user-guide.md#writing-a-schema) to indicate that a field must be in a document.

`required()` has no return value.

Parameter | Description
----------|------------
`field`   | Required. The name of the field you want to validate. You can specify [nested fields](user-guide.md#nested-fields) using the `.` separator, e.g. `author.last_name`. You can specify [list elements](user-guide.md#lists) using the `[]` suffix, e.g. `genres[]`.
`type`    | Optional. The [type](#type-validators) the field should have.

Depending on the [type](#type-validators) you specify, you can pass extra named parameters to `optional()`. For example, if a field is of type `string`, you can pass a `regex` parameter.

### validate

Runs the validator on the specified document using the specified schema.

`validate()` returns a list of `Message` objects, where each object indicates a validation error in the document.

Parameter | Description
----------|------------
`schema`  | Required. The [schema definition](user-guide.md#writing-a-schema). This must be a function that accepts no parameters and returns no value. Okay gives no guarantees about when or how often this function will be called.
`document` | Required. The document you want to validate. This must be a `dict`.
`message_values` | Optional. A dictionary with key-value pairs that the validator will add to all `Message` objects it produces.

## Classes

### Message

Represents a validation message, giving information about a validation error.

Each `Message` object has a `type` property, but beyond that, the available properties depend on the [validation message type](#validation-messages). The table below lists properties used by Okay, but custom validation messages may contain any property.

Property | Description
---------|------------
`type`   | Required. A string indicating why validation failed. Okay uses a limited set of [validation message types](#validation-message), but you are free to create any type you want.
`field`  | Optional. The name of the field that failed validation. This is present in all validation messages Okay produces, but you have the option to create a `Message` object without it, for example to indicate that a document failed to parse.
`expected` | Optional. Indicates why a field failed to validate. For example, if a number is too large, `expected` will contain the maximum allowed value, and if a string doesn't match a regular expression, `expected` will contain the pattern the field must match.

### SchemaError

The exception raised when there's a problem with the [schema definition](user-guide.md#writing-a-schema), for example a bug in a [custom validator](#user-guide.md#custom-validators), or an invalid [validation type](#type-validators). If `SchemaError` was raised in response to another exception, that other exception is available from the `__cause__` property of the `SchemaError` instance.

## Type validators

### any

The value can be of any type. This is the same as not specifying a type, unless you make it nullable.

### bool

The value must be a boolean, i.e. either `True` or `False`.

### custom

The value must pass validation as specified by a custom validator. This is useful when Okay's provided type validators don't fit your use case and you want to write your own validation logic.

Parameter | Description
-----------|------------
`validator` | Required. The function that will validate the value. It must accept two parameter: the field name and the field value. It must return `None` if validation succeeds or a [`Message`](#message) object if validation fails.

### int

The value must be a whole number. In terms of Python types, any `int` will fit the bill, and it's also fine if the value is a `float`, as long as the fractional part is 0.

Parameter | Description
-----------|------------
`min`      | The smallest allowed value.
`max`      | The largest allowed value.

### list

The value must be a list.

Parameter | Description
-----------|------------
`min`      | The smallest allowed list size.
`max`      | The largest allowed list size.

### number

The value must be a number. In terms of Python types, any `int`, `float`, or `Decimal` will do.

Parameter | Description
-----------|------------
`min`      | The smallest allowed value.
`max`      | The largest allowed value.

### object

The value must be an object, i.e. a Python `dict`.

### string

The value must be a string. It's not good enough if the value can be converted to a string, it must actually be of type `str`.

Parameter | Description
----------|------------
`regex`   | The regular expression pattern that the value must match.
`options` | A list of allowed values. The value must exactly match one of the options.
`case_sensitive` | `True` if options are case sensitive, `False` otherwise. Default is `True`. Note that `case_sensitive` doesn't apply to regular expressions. If you want your regular expression to be case insensitive, add the [inline flag](https://docs.python.org/3/library/re.html#index-15) `(?i)` to your pattern.

If you provide both `regex` and `options`, the value must match either. In other words, `options` are considered exceptions to the `regex`. If the value doesn't match `regex` and is not in `options`, the resulting validation message is [`no_match`](#no_match).

## Validation messages

### invalid_string_option

The field doesn't match any of the allowed strings.

Property   | Description
-----------|------------
`type`     | `invalid_string_option`
`field`    | The name of the field that failed validation.
`expected` | The list of acceptable strings.

### invalid_type

The field doesn't match the specified type.

Property   | Description
-----------|------------
`type`     | `invalid_type`
`field`    | The name of the field that failed validation.
`expected` | The name of the type the field should have.

### no_match

The field doesn't match the required regular expression.

Property   | Description
-----------|------------
`type`     | `no_match`
`field`    | The name of the field that failed validation.
`expected` | The regular expression pattern the field should match.

If you [provided both `regex` and `options`](#string) in your validation rule, the resulting message is slightly different.

Property           | Description
-------------------|------------
`type`             | `no_match`
`field`            | The name of the field that failed validation.
`expected.regex`   | The regular expression pattern the field should match.
`expected.options` | The list of acceptable exceptions.

### null_value

The fields contains `null`, even though it's not allowed to.

Property   | Description
-----------|------------
`type`     | `null_value`
`field`    | The name of the field that failed validation.
`expected` | The expected type of the field. Only present if a type was specified for the field.

### number_too_large

The field contains a number larger than the allowed maximum.

Property   | Description
-----------|------------
`type`     | `number_too_large`
`field`    | The name of the field that failed validation.
`expected` | The maximum value allowed.

### number_too_small

The field contains a number smaller than the allowed minimum.

Property   | Description
-----------|------------
`type`     | `number_too_small`
`field`    | The name of the field that failed validation.
`expected` | The minimum value allowed.

### too_few_elements

The list contains fewer elements than the allowed minimum.

Property   | Description
-----------|------------
`type`     | `too_few_elements`
`field`    | The name of the field that failed validation.
`expected` | The minimum number of elements the list should have.

### too_many_elements

The list contains more elements than the allowed maximum.

Property   | Description
-----------|------------
`type`     | `too_many_elements`
`field`    | The name of the field that failed validation.
`expected` | The maximum number of elements the list may have.