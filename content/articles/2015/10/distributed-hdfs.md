
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

    TODO: hdfs cp nyctaxi.csv /data/nyctaxi/

and we query the namenode to find out what just happened.

Java project just use the HDFS Java library.  We'd like to avoid JVM dependence
so instead we depend on Spotify's
[snakebite](http://snakebite.readthedocs.org/en/latest/) library, which
includes the Protobuf headers necessary to interact with the namenode.

The library code within Snakebite doesn't support exactly this query, and so
we use their protobuf headers and some write custom code (written by
[Ben Zaitlen](https://github.com/quasiben) and
[Martin Durant](https://github.com/martindurant/)) available
[here](https://github.com/mrocklin/distributed/blob/master/distributed/hdfs.py).

>>> from distributed import hdfs
>>> blocks = hdfs.get_locations('/data/nyctaxi/', '192.168.1.100', 9000):
>>> blocks
TODO

So we see that our single file, TODO, has been turned into many small
files/blocks, each of which is replicated across three machines.  We can even
go and inspect these blocks.

$ ssh hostname  TODO
$ head filename TODO
TODO

Once we have block locations on the host file system we ditch HDFS altogether
and revert to our normal model of the world.


Data-local tasks with distributed
---------------------------------

So lets load all of these blocks with Pandas and distributed.

>>> columns = [TODO]

>>> from distributed import Executor
>>> executor = Executor('192.168.1.100:8787')
>>> dfs = [executor.submit(pd.read_csv, block['path'], workers=block['hosts'],
...                        columns=columns, skipinitialspace=True)
...        for block in blocks]

We use the `workers=` keyword argument to `Executor.submit` to restrict these
jobs so that they can only run on the hosts whose local file systems actually
hold these paths.  Also, because only the first block will have column
information we've had to provide keyword arguments directly to the
`pd.read_csv` call.


Some simple analysis
--------------------

We can now do some simple work, like counting all of the passenger counts
values.

>>> counts = executor.map(lambda df: df.passenger_count.value_counts(), dfs)
>>> total = executor.submit(sum, counts)
>>> total.result()
TODO


Conclusion
----------

We used `snakebite`'s protobuf definitions and `distributed`'s data-local task
scheduling to run Pandas directly on CSV data in HDFS.  Our approach wasn't
elegant or streamlined but it also wasn't terribly complex.  None of Snakebite,
distributed, nor Pandas was designed for this use case and yet we were able to
compose them together to achieve something that previously only monolithic
frameworks (Hadoop, Spark, Impala) have managed.  HDFS no longer feels like
"big data magic"; it's just a way that big files get split up into smaller
files on many machines that we need to track down to run our normal toolset.

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
