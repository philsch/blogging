Monitor your GraphQL Apollo Server in Google Cloud
==================================================

Blog article: (URL HERE)

Used gists:

* https://gist.github.com/philsch/1f70623410016400d1fb34f964aef750
* https://gist.github.com/philsch/b7d451b740b73437788a0d0a15ddf677
* https://gist.github.com/philsch/adce29d2f7f59f6bcbba432c4a34a12f

## apollo1

Apollo GraphQL Server 1 example without any error handling. There to demonstrate that
no graphQL errors are automatically picked up by *Google App Engine*.

## apollo2

Apollo GraphQL Server 2 example with error handling. To create an unexpected exception 
add some wrong code e.g. `let tmp = args.books.length;` to the resolver in `book.js`.