
# ArticulateORM

## Summary

Articulate is an ORM that makes it very easy to work with database information in Python. Consider the following example:

```python
user.where('user_id', 'huskyct').enrollments().select('course_id', 'user_id', 'role).get()
```

This would fetch every course that the 'huskyct' user is enrolled in, and will return a collection of the user models. This allows you to easily work with the data with very little overhead.

It is very easy to define relationships between tables using Articulate.

## Inspiration

Articulate is modeled largely after Laravel Eloquent ORM. However, it has some notable differences.

## Primary Key

Articulate expects your tables to have a primary key of 'PK1'. If this is not the case, you can use the overrides function to set a different value for your primary key. This method is documented later in this document.

## Table name

Articulate expects table names to be the name of the class + s. Your class names should be singular in name, Articulate will create the name automatically. If this is not the name of your table, you can set this with the overrides method, discussed later in this document.

## Overrides

The overrides method is an easy to use way to set default values for your objects.

```python
class User(BaseModel):
	def overrides(self: object):
		self.table_name = "all_users"
		self.primary_key = 'id'
```

In this example, the name of the users table is "all_users", and the primary key is "id".

## Casting

Object attributes can be cast to different types by use of the casts method. Take the following example:

```python
class User(BaseModel):
	def casts(self: object):
		return {
			'age': int
		}
```

This example will cast the age attribute to an integer. 

**IMPORTANT**

Casting only works when the model has been created from a named tuple. This happens automatically when results are returned from the database. However, if you create the instance manually, casts() will not be called, and it is up to you to cast your attributes as needed.

## Relationships

*NOTE*: When using relationships, Articulate will complain if two columns have the same name. You can work around this by simply using select() to choose the columns you want, and alias columns as needed.

```python
user = User()
user.where('firstname', 'Bob').phones().select('user_id', 'phone_id', "'user.id' as user_pk1").get()
```

### One to One

A one-to-one relationship is a very basic type of database relationship. For example, a User model might be associated with one Phone model. To define this relationship, we will place a phone method on the User model. The phone method should call the hasOne method and return its result. The hasOne method is available to your model via the model's BaseModel class:

```python
class User(BaseModel):
	def phone(self: object):
		return self.hasOne(Phone)
```

### One to Many

A one-to-many relationship is used to define relationships where a single model is the parent to one or more child models. For example, a blog post may have an infinite number of comments. Like all other Eloquent relationships, one-to-many relationships are defined by defining a method on your Eloquent model:

```python

class Post(BaseModel):
	def comments(self: object):
		return self.hasMany(Comment)
```

Once the relationship has been identified, you can access the comments of a post by simply accessing that method:

```python
post = Post.where('title', 'Super Awesome Post').comments().get()
```


