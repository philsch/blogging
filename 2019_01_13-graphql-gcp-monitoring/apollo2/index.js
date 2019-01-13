const express = require('express');
const {ApolloServer, ApolloError} = require('apollo-server-express');
const DatabaseError = require('./errors/DatabaseError');
const {ErrorReporting} = require('@google-cloud/error-reporting');

const {resolvers, typeDefs} = require('./books');

const PORT = 8080;
const errorReporting = new ErrorReporting();

const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: true,
  playground: true,
  formatError: (error) => {

    /*
     * Database connection error should appear in logs
     * but not in Error Report as this is not considered a bug
     */
    if (error.originalError instanceof DatabaseError) {
      console.error('Database error occurred', error);
      return error;
    }

    /*
     * Some other Apollo error like wrong user input
     * we don't need to log or report this,
     * but still return the error back to the client
     */
    if (error.originalError instanceof ApolloError) {
      return error;
    }

    /*
     * Something unexpected is wrong
     */
    errorReporting.report(error.originalError.stack); // report to Google Error Report
    console.error(error); // log the error
    return {message: 'Internal Server Error'} // do not reveal error details to the client


  }
});
const app = express();
server.applyMiddleware({app, path: '/graphql'});

app.listen(PORT);