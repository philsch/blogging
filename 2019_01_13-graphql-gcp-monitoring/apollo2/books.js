const DatabaseError = require('./errors/DatabaseError');

const exampleBooks = [
  {title: "Book A", author: "Chelsey Stevens"},
  {title: "Book B", author: "Chelsey Stevens"},
  {title: "Book C", author: "Corinne Hogg"},
];

const typeDefs = `
  type Query {
    books(author: String): [Book]
  }
  
  type Book {
    title: String
    author: String
  }
`;

const simulateDbDown = async () => {
  if (Math.random() > 0.7) {
    throw new DatabaseError('[TEST] Oh no the database is down!');
  }
};

const resolvers = {
  Query: {
    books: async (parent, args) => {
      await simulateDbDown();

      let tmp = args.books.length;

      if (!args.author) {
        return exampleBooks;
      }

      return exampleBooks.filter((el) => el.author === args.author);
    }
  }
};

module.exports = {typeDefs, resolvers};