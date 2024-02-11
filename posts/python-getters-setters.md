---
title: "Python getters and setters"
date: 2022-02-21
categories: ["python"]
draft: false
---

# Python getters and setters

If you have ever worked with a language such as Java, the concept of _getter_ or
_setter_ won't be foreign to you. If you haven't, _getters_ and _setters_ are
methods which let you access and modify class attributes; usually where you
wouldn't have access otherwise because of the restricting _scope_. It may then
come as a surprise that Python, where all members are public, also has a concept
of _getters_, _setters_ and _deleters_.

I'd like to cover how to use _getters_ and _setters_ in Python as well as the
proper way to manage attributes.

The following won't be exhaustive, there are details and subtleties to Python
which you will find in the [Resources](#resources) section.


## Attributes and where to find them {#attributes-and-where-to-find-them}

When creating a custom class in Python, an instance's namespace is stored in a
dictionary object, which can be accessed with the `__dict__` attribute. In a
basic class, accessing an attribute is merely a lookup in the dictionary to
retrieve to value of the attribute, if it exists.

Let's practice and build a `Person` object with a name and an age.

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("Lenny", 34)
```

Since there is no concept of private instance variables in Python, the class
attributes are exposed and we can access them directly. We can also use the
dictionary which stores the attributes and grab them from there. The following
expressions are equivalent.

```python
print(person.name, person.age) # prints Lenny 34
print(person.__dict__["name"], person.__dict__["age"]) # prints Lenny 34
```

It also means that there is no protection around attributes, they can be
modified through assignment, even erroneously.

```python
person.name = "Jenny"
person.age = 45
print(person.name, person.age) # prints Jenny 45
```

If you want to signal to other developers that they should not modify an
attribute because it is implementation specific or will be subject to change
internally, you can add an underscore before its name. Note that it does not
change anything in practice but it's a commonly accepted convention in Python.

We can update our class definition and signal we do not want a person's name to
be changed. We can still access the attributes in the same way as above, it is
strictly a cosmetic change.

```python
class Person:
    def __init__(self, name, age):
        self._name = name
        self.age = age

person = Person("Jack", 67)

print(person._name, person.age) # prints Jack 67
print(person.__dict__["_name"], person.__dict__["age"]) # prints Jack 67
```

Another function of getters and setters in languages such as Java or C++, aside
from [encapsulation](https://en.wikipedia.org/wiki/Encapsulation_(computer_programming)), is to check for attribute validity. The current way of
accessing attributes does not allow any kind of validation; there must be a
better way!


## Properties {#properties}

Earlier, I said that accessing an instance attribute gets the value from the
instance's `__dict__` but we can wrap this access with an function call that
provides additional capabilities. More precisely, we use the `property()`
class to create [a descriptor](https://docs.python.org/3/glossary.html#term-descriptor). A **descriptor** lets you customize how access,
storage and deletion happen in an object, which we will make use of in the
following example. The specific way of calling `property()` prefixed with the
`@` symbol is called [a decorator](https://docs.python.org/3/glossary.html#term-decorator) and is worth a post in and of itself. Know at least
that it's usually used to add functionalities to a Python object. Here, we use
it to change how the attribute behaves upon access/storage/deletion.

Using properties is useful, for example, when an attribute is re-computed on
access, to verify if an attribute assignment checks some conditions, to manage
complex deletions, etc. But they also have a downside: more code and more
overhead, which is why you probably shouldn't use them for trivial classes. Now
that you're warned, onto our example once more.

Let's update the `Person` class to use properties and check that the age is not
negative when it is set. Here's a breakdown of what's happening:

-   At initialization, attributes have an underscore, this signifies that outside
    the inner working of the class, we should not directly access those.

-   A `@property` decorator is added and it wraps a function that has the name of
    the attribute without underscore. This acts as the getter and this case we
    simply return the value without added logic.

-   A `@age.setter` decorator is added, it also bears the name of the attribute
    without underscore and takes another parameter: the new value of the `age`
    attribute. The body of the function checks that the attribute is not negative
    and raises an error if it is.

-   A `@age.deleter` decorator is added, which is less often used but makes
    attribute deletion possible.

-   No `@name.setter` is added, which means that trying to set the name to a new
    value will fail.

<!--listend-->

```python
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new_age):
        if new_age <= 0:
            raise ValueError(f"new_age should be positive but received: {new_age}")
        else:
            self._age = new_age

    @age.deleter
    def age(self):
        del self._age

person = Person("John", 31)
person.name = "Frank" # AttributeError: can't set attribute 'name'
person._name = "Frank" # Works but you shouldn't do that
person.age = 0 # ValueError: new_age should be positive but received: 0
person._age = 0 # Works but you shouldn't do that
del person.age # Deletes the _age attribute
person.age # Now raises AttributeError: 'Person' object has no attribute '_age'
```

There is a flaw here though, the age of a person isn't checked at initialization
and as such:

```python
person = Person("Malthus", -1)
```

is valid code in our implementation. We can fix this though by calling the
setter inside `__init__`. This adds one line of code, we can't get rid of the
first underscored assignment because the object otherwise doesn't know where to
look for the attribute.

```python
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age
        self.age = age # Mind the lack of underscore!

   #... rest of the class' body
```

Now, the previous line with an invalid argument will raise a `ValueError`.


### Property inheritance {#property-inheritance}

Properties' behavior does carry in sub-classes. For example, an `Employee` class
inheriting from the `Person` class will also benefit from the getters, setters
and deleters of the parent class.

```python
class Employee(Person):
    def __init__(self, name, age, salary):
        super().__init__(name, age)
        self._salary = salary

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, new_salary):
        if new_salary <= 0:
            raise ValueError(f"Salary must be positive but received: {new_salary}")
        elif new_salary >= 1_000_000:
            raise ValueError("Not allowed by the payroll software.")
        else:
            self._salary = new_salary
```


## Using properties in the wild {#using-properties-in-the-wild}

A slightly more involved example of using a property is when we want to
recompute a value on access because it might have changed since the last access.

For example, we might want to keep track of our employees in an `EmployeeList`
that will give us aggregate information about our work force. In more complex
settings, one would use a spreadsheet but nothing keeps you from using objects,
which has the benefit of introducing no new dependencies.

```python
class EmployeeList:
    def __init__(self, *args):
        self.employees = args
        self._total_salaries = 0
        self._avg_age = 0

    @property
    def total_salaries(self):
        self._compute_salaries()
        return self._total_salaries

    @property
    def avg_age(self):
        self._compute_avg_age()
        return self._avg_age

    def _compute_salaries(self):
        self._total_salaries = sum(e.salary for e in self.employees)

    def _compute_avg_age(self):
        self._avg_age = sum(e.age for e in self.employees) / len(self.employees)


employee_list = EmployeeList(
    Employee("Jenna", 30, 31_000),
    Employee("Fred", 57, 40_000),
    Employee("Mary", 45, 60_000),
)

print(employee_list.avg_age, employee_list.total_salaries) # 44.0 131000
```

If the recomputing is very expensive (in time or memory) you can add a boolean
value that acts as a guard of sorts and which can be modified by another
function or object. It amounts to a few checks like so:

```python
class EmployeeList:
    def __init__(self, *args):
        self.employees = args
        self._total_salaries = 0
        self._avg_age = 0
        self.salary_recompute = True
        self.avg_age_recompute = True

    @property
    def total_salaries(self):
        if self.salary_recompute:
            self._compute_salaries()
            self.salary_recompute = False
        return self._total_salaries

    @property
    def avg_age(self):
        if self.avg_age_recompute:
            self._compute_avg_age()
            self.avg_age_recompute = False
        return self._avg_age

    def _compute_salaries(self):
        self._total_salaries = sum(e.salary for e in self.employees)

    def _compute_avg_age(self):
        self._avg_age = sum(e.age for e in self.employees) / len(self.employees)
```

Now, adding or removing employees should update the recomputing flags to ensure
that those costly operations are only computed when needed.

This last example concludes the post, I hope you had fun reading it!


## Conclusion {#conclusion}

Properties help you manage attributes in Python objects at the cost of some
overhead. They are most useful when attributes often change over times or over
operations and when attributes assignment needs to be checked. If such
operations are not required by your classes then you probably don't need to use
them.


## Resources {#resources}



-   [Python classes documentation](https://docs.python.org/3/tutorial/classes.html)

-   [Python descriptor guide](https://docs.python.org/3/howto/descriptor.html#id1)

-   [Python properties documentation](https://docs.python.org/3/library/functions.html?highlight=property#property)

-   Anything written by [Raymond Hettinger](https://twitter.com/raymondh).