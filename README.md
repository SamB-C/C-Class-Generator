# C++ Class Generator

## Description

This program takes an emmet like description of a C++ class, and creates a `.hpp` and `.cpp` file, containing boilerplate for that class.

Navigation:

- [Emmet Structure](#description)
- [Defining Member Variables](#description)
  - [Member Variable Names](#member-variable-names)
- [Inheritance](#inheritance)
- [Templates](#templates)
  - [Include Guards](#include-guards)
  - [Basic Templates](#basic-templates)
  - [Class Specialisation](#class-specilisation)
- [Non-Basic Types](#non-basic-types)

## Emmet Structure

The emmet must be in the format `{className};{member variables}`. `className` is the name of the class to be created. The two files created will be `{className}.hpp` and `{className}.cpp`.

### Defining Member Variables

The member variable section is in the format `gs{num1}{type1}{num1}{type1}`.
For each type specified, a number of private member variables given by the preceding number, are made of that type. For example, `4int` would create 4 integer member variables.  
These can be chained together to specify how many of each type need to be created. For example `4int3float` would create 4 integers and 3 floats.

The presence or exclusion of `g` and `s` at the beginning indicate whether getters and/or setters respectively should be created for these member variables. For example, `g4int3float` would, after creating the member variables, also declare and define getters and setters for those 4 ints and 3 floats.  
The getters are in the format:

```cpp
// For an member variable X of type int
int get_X() const
{
    return X;
}
```

The setters pass by reference and are in the format:

```cpp
// For an member variable X of type int
void set_X(const int &newX)
{
    X = newX;
}
```

If some member variables need getters and setters and some don't, extra member variable sections can be appended to the emmet: `{className};{member variables};{member variables}`. For example, a complete emmet `Animal;gs1int2float;s1double;5int` would create:

- 1 integer with both a getter and setter
- 2 floats with both a getter and setter
- 1 double with just a setter
- 5 integers with neither a getter or a setter

#### Member Variable Names

Member variables are given an automatically generated name in the format `attr{index}_g_s`, where index indicates the order that the attributes were created. `_g` and `_s` are only present if the member variable has a getter and/or setter respectively.  
All instances of this variable name (including the `newX` in the setters), follow this format, allowing you to quickly refactor this name by selecting all instances of it within your code.

### Inheritance

Inheritance is in the format `{className}{symbol}{parentClassName}?`.
The symbol indicates what form of inheritance is used for the following parent class.

| Symbol | Inheritance Type |
| ------ | ---------------- |
| `+`    | Public           |
| `-`    | Private          |
| `=`    | Protected        |

The presence of `?` after the parent class name indicates whether or not the inheritance should be virtual.

Inheritance can also be chained for multiple inheritance, where the order of inheritance is maintained from the emmet.

For example, `Mule=Horse?+Donkey` would create a class declaration of:

```cpp
class Mule : virtual protected Horse, public Donkey
```

Parent classes are automatically included in the `.hpp` file in the format `#include "{ParentClass}.hpp"`.

### Templates

The generator can also generate template classes. As template classes must be defined where they are declared, only a `.hpp` file containing the entire class is created.

#### Include guards

To obey the one definition rule, in the case where the class is a template, the `.hpp` file will create the following include guards:

```cpp
// For a class XXX
#ifndef XXX_HPP
#define XXX_HPP

// Class defined here

#endif
```

#### Basic Templates

The syntax for creating the class as a template is `{className}<>;{member variables}`, with the `<>` indicating that the class is a template (please note this is reversed from creating template specialisations). At this time, only a single template can be created, and this template is automatically `T`, which is important when creating member variables using this type.

The resulting class from the emmet `Animal<>;s1T` looks like:

```cpp
#ifndef ANIMAL_HPP
#define ANIMAL_HPP


template <typename T>
class Animal
{
private:
	T attr0_s;

public:
	void set_attr0_s(const T &newattr0_s)
    {
		attr0_s = newattr0_s;
	};
};

#endif
```

#### Class Specilisation

To create a specialised template, specify the type you wish to specialise within the `<>`.

For example, to create a specialised `Animal`, (see [Basic Templates](#basic-templates)) for an int, the emmet `Animal<int>;s1int` will produce:

```cpp
#ifndef ANIMAL_HPP
#define ANIMAL_HPP


template <>
class Animal<int>
{
private:
	int attr0_s;

public:
	void set_attr0_s(const int &newattr0_s)
    {
		attr0_s = newattr0_s;
	};
};

#endif
```

### Non-basic types

If the types `string` or `vector`, or the types of any smart pointer (with or without `std::` prepended) are given as a member variable type then those types are automatically included. If `std::` is omitted in at least one instance of these types, the appropriate namespace is used (e.g. `using std::string;`).
For example, if a member variable is defined with type `string` in the emmet, then the following lines will be written to the `.hpp` file:

```cpp
#include <string>
using std::string;
```

And in the `.cpp` file:

```cpp
using std::string;
```

Nested types are supported.

## TO DO

- Allow user to input a target file location
- If process will override file, check with user if this is intended. Give option to append to hpp file (in case of template specilisation)
- Include `.hpp` files of parent classes
- Multiple template classes.
- Consider case where there are no member variables
- Fill in example in `README.md`
