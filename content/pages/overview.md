Title: Overview

The Blaze ecosystem is a set of libraries that help users store, describe, query and process data.

## Data Processing Systems

There are three components in a data processing system: Data, Expressions and Computational Engines.

- **Data** can have different structure (tabular, nested or unstructured), live in different containers
    and formats (e.g. csv, parquet, avro, compressed), and contain different information about itself or also
    called metadata (e.g. column names, variable types).

- **Expressions** are the syntax, API or language used to define a query or transformation to be
    computed on the data.

- **Computational Engines or Backends** are the executors of those expressions on some data (e.g.
    database engine, Python libraries).


The following characteristics can define a particular Data Processing System:

- **Metadata** that describes the structure and content of data in the system
- **Compression** and **access** to data
- **Performance** of the computational engine or backend
- **Expressiveness** and **simplicity** of the language or API


## The Blaze Ecosystem

The goal of the Blaze ecosystem is to simplify data processing for users by providing:

- A common language to describe data that it's independent of the Data Processing System, called
[**datashape**](http://blaze.github.io/pages/projects/datashape).
- A common interface to query data that     it's independent of the Data Processing System, called
[**blaze**](http://blaze.github.io/pages/projects/blaze).
- A common utility library to move data from one format or system to another, called
[**odo**](http://blaze.github.io/pages/projects/odo).
- Compressed column stores, called [**bcolz**](http://blaze.github.io/pages/projects/bcolz) and
[**castra**](http://blaze.github.io/pages/projects/castra).
- A parallel computational engine, called [**dask**](http://blaze.github.io/pages/projects/dask).


## Learn more

The project repositories can be found under the [Github Blaze Organization](https://github.com/blaze). Feel free to
reach out to the Blaze Developers through our mailing list, blaze-dev@continuum.io.