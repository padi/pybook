import cherrypy
from Cheetah.Template import Template
from sqlobject import *

# configure your database connection here
__connection__ = 'mysql://root:@localhost/test'

class Book(SQLObject):
    title  = StringCol(length = 50, notNone = True)
    author = StringCol(length = 30, notNone = True)

    # def __init__(self, title, author):
    #     self.title = title
    #     self.author = author
    #     self.status = 'ACTIVE'
    
    def to_dict(self):
        return {
            'id' : self.id,
          'title': self.title,
          'author': self.author
        }

class BookManager:
    # cherrypy.request.json
    def index(self):
        books = Book.select()

        template = Template('''
            <h2>Books</h2>

            <div id="book-form">
              <h2>Add Book</h2>
              <form action="/books" method="post">
                <input type="text" name="title" placeholder="title">
                <input type="text" name="author" placeholder="author">
                <input type="submit" value="Add Book via backbone">
              </form>
            </div>

            <h2>Books Added via BackBone</h2>

            <ul id="bookmarks"></ul>

            <ul id="books-list">
            #for $book in $books
                <li>
                    $book.title, <br/>
                    $book.author <br/>
                    [<a href="./edit?id=$book.id">Edit</a>] <br/>
                    [<a href="./delete?id=$book.id">Delete</a>] <br/>
                </li>
            #end for
            </ul>

            <p>[<a href="./edit">Add book</a>]</p>


            <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js"></script>
            <script src="http://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.2.1/underscore-min.js"></script>
            <script src="http://cdnjs.cloudflare.com/ajax/libs/backbone.js/0.5.3/backbone-min.js"></script>
            <script src="/books.js" type="text/javascript"></script>
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

    # RESTFul method for Backbone.js use
    @cherrypy.tools.json_in(on = True)
    @cherrypy.tools.json_out(on = True)
    def books(self, book_id=None):

        request = cherrypy.request
        if request.method == 'GET' and not book_id:
            # query all books, search for sqlobject query and store it in bookmarks
            books = Book.select()
            return [b.to_dict() for b in books]

        elif book_id:
            # get book based on id
            book = Book.get(int(book_id))
            if not book:
                abort(404)

        if request.method == 'POST':
            # create new book
            book = Book(
                title = request.json['title'],
                author = request.json['author']
            )

        elif request.method == 'PUT':
            # edit book
            book.set(
                title = request.json['title'],
                author = request.json['author']
            )

        elif request.method == 'DELETE':
            # delete book
            book = Book.get(int(id))
            book.destroySelf()

        return book.to_dict()
    books.exposed = True


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