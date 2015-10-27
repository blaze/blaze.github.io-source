Outline
-------

1.  Describe HDFS
2.  Motivate talking directly to datanodes
3.  Use snakebite to query locations of blocks
4.  Use distributed to submit jobs directly on those blocks
5.  Use snakebite+distributed+pandas to process CSV files on HDFS in Pure
    Python


HDFS Summary
------------

The Hadoop File System (HDFS) distributes large datasets across many data
nodes roughly as follows:

1.  Cut up large files into 64MB blocks (or thereabouts)
2.  Replicate each block on a few data-nodes (to provide resilience to
    machine loss)
3.  Store all block/datanode locations on a central namenode

Normally we don't think about the internal structure.  We move large files in
and out via the namenode or we use frameworks like Hadoop and Spark to interact
with the data blocks on our behalf.  Both Hadoop and Spark are JVM tools though
and provide somewhat suboptimal Python experiences.


Direct Datanode Interaction
---------------------------

Efficient computation on data in HDFS requires dealing directly with data nodes.

When we copy data into or out of HDFS with the `hdfs` command line utility or
with WebHDFS (e.g. through Hue) we interact with the master namenode. This
namenode insulates us from the sea of datanodes that actually hold the data.
This is great because we get a comprehensive view of the file system without
having to muck about with the individual blocks.  All of the data flows through
one, easy-to-understand centralized point, the namenode.

Unfortunately if we want to compute on the data then we don't want to pull
everything through the central namenode; we want to work with each block
directly on one of the data nodes where it currently lives.

This is what computational systems like Hadoop/Spark/Impala do.  If we want
efficient data local computation on HDFS then its what we'll have to do too.


Query Block Locations with Snakebite
------------------------------------

So we put a dataset on an HDFS instance:

    $ hdfs cp nyctaxi.csv /data/nyctaxi/   TODO

and we query the namenode to find out what just happened.

Java projects use the HDFS Java library.  We avoid JVM dependence and so
instead use Spotify's
[snakebite](http://snakebite.readthedocs.org/en/latest/) library, which
includes the Protobuf headers necessary to interact with the namenode directly.

The library code within Snakebite doesn't support our desired queries, and so
we use their protobuf headers to write custom code available
[here](https://github.com/mrocklin/distributed/blob/master/distributed/hdfs.py)
(work done by [Ben Zaitlen](https://github.com/quasiben) and
[Martin Durant](https://github.com/martindurant/)).

```python
>>> from distributed import hdfs
>>> blocks = hdfs.get_locations('/data/nyctaxi/', '192.168.1.100', 9000):
>>> blocks
TODO
```

So we see that our single file, TODO, has been turned into many small
files/blocks, each of which is replicated across three machines.  We can even
go and inspect these blocks.

```
$ ssh hostname  TODO
$ head filename TODO
TODO
```

Once we have block locations on the host file system we ditch HDFS and just
think about remote hosts that have files on their local file systems.  HDFS has
played its part and can exit the stage.


Data-local tasks with distributed
---------------------------------

We load these blocks with `pandas` and `distributed`.

```python
>>> columns = [TODO]

>>> from distributed import Executor
>>> executor = Executor('192.168.1.100:8787')
>>> dfs = [executor.submit(pd.read_csv, block['path'], workers=block['hosts'],
...                        columns=columns, skipinitialspace=True)
...        for block in blocks]
```

We use the `workers=` keyword argument to `Executor.submit` to restrict these
jobs so that they can only run on the hosts whose local file systems actually
hold these paths.  Also, because only the first block will have the CSV header
we provide keyword arguments directly to the `pd.read_csv` call.


Some simple analysis
--------------------

We now do some simple work, counting all of the passenger counts values.

```python
>>> counts = executor.map(lambda df: df.passenger_count.value_counts(), dfs)
>>> total = executor.submit(sum, counts)
>>> total.result()
TODO
```

We see that TODO...


Conclusion
----------

We used `snakebite`'s protobuf definitions and `distributed`'s data-local task
scheduling to run Pandas directly on CSV data in HDFS.  We didn't touch the JVM
nor did we invent a whole new framework but instead reused existing components.

Our approach wasn't elegant or streamlined but it also wasn't terribly complex.
None of Snakebite, distributed, nor Pandas was designed for this use case and
yet we were able to compose them together to achieve something that previously
only monolithic frameworks (Hadoop, Spark, Impala) have managed.  HDFS no
longer feels like "big data magic"; it's just a way that big files get split up
into smaller files on many machines that we need to track down to run our
normal toolset.

That's not to disparage frameworks or elegant streamlined approaches.  If
enough people care about this sort of thing then I may hook up
[dask.dataframe](https://dask.pydata.org/en/latest/dataframe.html) to this in
the near future.

Questions
---------

I'm pretty ignorant when it comes to the JVM HDFS stack.  It'd be great to find
some people out there who are interested by the approach above and knowledgeable
in Hadoop internals that are willing to provide guidance.

*  Are we going down the right path using Snakebite/protobufs to interact with
   the namenode?  Should we be doing something else?  `libhdfs` or `webhdfs`
   maybe?
*  What about writing blocks to HDFS?
*  Is there some danger in sidestepping HDFS in this manner?
