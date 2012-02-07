import cherrypy
from Cheetah.Template import Template
from sqlobject import *

# configure your database connection here
__connection__ = 'mysql://root:@localhost/test'

class Book(SQLObject):
    title  = StringCol(length = 50, notNone = True)
    author = StringCol(length = 30, notNone = True)

class BookManager:
    def index(self):
        books = Book.select()

        template = Template('''
            <h2>Books</h2>

            <ul>
            #for $book in $books
                <li>
                    $book.title, $book.author
                    [<a href="./edit?id=$book.id">Edit</a>]
                    [<a href="./delete?id=$book.id">Delete</a>]
                <br/>
                </li>
            #end for
            </ul>

            <p>[<a href="./edit">Add book</a>]</p>
        ''', [locals(), globals()])

        return template.respond()
    index.exposed = True

    def edit(self, id=0):
        # we really want id as an integer. Since GET/POST parameters
        # are always passed as strings, let's convert it.
        id = int(id)

        if id > 0:
            # if an id is specified, we're editing an existing book.
            book = Book.get(id)
            title = "Edit Book"
        else:
            # if no id is specified, we're entering a new book.
            book = None
            title = "New Book"

        template = Template('''
            <h2>$title</h2>

            <form action="./store" method="POST">
                <input type="hidden" name="id" value="$id" />
                Title: <input name="title" value="$getVar('book.title', '')" /><br/>
                Author: <input name="author" value="$getVar('book.author', '')" /><br/>
                <input type="submit" value="Store" />
            </form>
        ''', [locals(), globals()])

        return template.respond()
    edit.exposed = True

    def delete(self, id):
        # Delete the specified book
        book = Book.get(int(id))
        book.destroySelf()
        return 'Deleted. <a href="./">Return to Index</a>'
    delete.exposed = True
    
    def store(self, title, author, id = None):
        if id and int(id) > 0:
            book = Book.get(int(id))

            book.set(
                title = title,
                author = author)
        else:
            book = Book(
                title = title,
                author = author)

        return 'Stored. <a href="./">Return to Index</a>'
    store.exposed = True

    def reset(self):
        Book.dropTable(True)
        Book.createTable()
        Book(
            title = 'Harry Potter',
            author = 'J.K. Rowling')

        return "reset completed!"
    reset.exposed = True

print("If you're running this application for the first time, please go to http://localhost:8080/reset once in order to create the database!")
cherrypy.quickstart(BookManager())