const {ApolloError} = require('apollo-server-express');

class DatabaseError extends ApolloError {
  constructor(...args) {
    super(...args);
  }
}

module.exports = DatabaseError;