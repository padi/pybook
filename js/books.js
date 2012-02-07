(function($) {
  // Model
  window.Book = Backbone.Model.extend({
    url: function() {
      // Make id optional because the create event uses the model's url and
      // since the model is just about to be created, it doesn't have an id yet
      return '/books' + (this.get('id') ? '/' + this.get('id') : '');
    }
  });

  // Collection
  window.Books = Backbone.Collection.extend({
    model: Book,
    url: '/books',
    // Determines sort key
    // Resetting a collection automatically sorts it
    comparator: function(model) {
      return model.get('title');
    }
  });

  // Book List Item View
  window.BookLi = Backbone.View.extend({
    // Specifying a `tagName` for a view automatically gives it a this.el which
    // contains an element with that `tagName`
    tagName: 'li',
    events: {
      // // Save on description change
      // 'change .desc': 'save',
      // Destroy when trashed
      'click .trash': 'destroy'
    },
    render: function() {
      // `toJSON` returns an object with the model's attributes
      var data = this.model.toJSON();
      // Add contents of li element
      $(this.el).html(
        $(  '<input type="text" class="desc" value="' + data.title + '">' +
            '<input type="text" class="desc" value="' + data.author + '">' +
            '<a href="#" class="trash">Trash</a>'
          )
      );
      // It's more of a convention to return the view object upon rendering
      return this;
    },
    // save: function(e) {
    //   // Save changes in description
    //   this.model.save({desc: $(e.target).val()});
    // },
    destroy: function(e) {
      // Destroying a model removes it from its collection but
      // doesn't remove the view's element
      // We have to do it ourselves upon success of delete request
      this.model.destroy({success: function(model) {
        $(model.view.el).remove();
      }});
    }
  });

  // Book List View
  window.BookList = Backbone.View.extend({
    initialize: function() {
      // These methods are called in the context of the Books collection
      // so we have to bind them manually to the view
      _.bindAll(this, 'add', 'reset', 'checkBlankState');
      // Instantiate a Books collection and set it as an attribute of the view
      this.books = new Books;
      // Bind collection events to view methods
      this.books.bind('add', this.add);
      this.books.bind('reset', this.reset);
      this.books.bind('add', this.checkBlankState);
      this.books.bind('remove', this.checkBlankState);
      this.books.bind('reset', this.checkBlankState);
    },
    // Add callbacks have the model added as first argument
    add: function(model) {
      model.view = new BookLi({model: model});
      $(this.el).append(model.view.render().el);
    },
    // Reset callbacks have collection reset as the first argument
    reset: function(collection) {
      $(this.el).empty();
      collection.each(this.add);
    },
    // I added this method just to show how you can utilize
    // collection event callbacks for other functions other than
    // representing/modifying models/collections
    checkBlankState: function(modelOrCollection) {
      var $el = $(this.el),
          // We don't know if the passed first argument is a model or collection
          // so let's check by looking for the collection attribute (w/c obviously
          // will be only present in models)
          collection = modelOrCollection.collection || modelOrCollection;
      // If collection is empty then show some blank state text
      if (collection.length == 0) {
        $el.append('<li class="empty">Don\'t be shy! Add books now. &rarr;</li>');
      // Else then remove the blank state text
      } else {
        $('.empty', $el).remove();
      }
    }
  });
  // Instantialize Book List View
  var bookList = new BookList({el: '#books'});

  // Fetch existing books from DB
  bookList.books.fetch();

  // Book Form View
  window.BookForm = Backbone.View.extend({
    events: {
      // Override the form submit with the view's create method
      'submit': 'create'
    },
    create: function() {
      // `serializeArray` produces a list of objects with name-value keys
      // We need a JSON representation of our model so we create it
      // from what we get from `serializeArray`
      var book = {},
          $el = $(this.el);
      _.each($el.serializeArray(), function(x) {
        if (x.name) {
          book[x.name] = x.value;
        }
      });
      // Add it to the Books collection we instantialized in the Book List View
      bookList.books.create(book, {success: function() {
        // Reset form
        $('input', $el).not('[type="submit"]').val('');
      }});
      // Return false to prevent the submit event from bubbling
      return false;
    }
  });
  // Instantialize Book Form View
  var bookForm = new BookForm({el: 'form'});
})(jQuery);