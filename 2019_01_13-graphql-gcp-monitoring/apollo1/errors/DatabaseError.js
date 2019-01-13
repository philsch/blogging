class DatabaseError extends Error {
  constructor(...args) {
    super(...args);
  }
}

module.exports = DatabaseError;