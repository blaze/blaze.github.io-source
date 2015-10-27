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

    $ hdfs dfs -cp yellow_tripdata_2014-01.csv /data/nyctaxi/

and we query the namenode to find out what just happened.

Java projects use the HDFS Java library.  We avoid JVM dependence and so
instead use Spotify's
[snakebite](http://snakebite.readthedocs.org/en/latest/) library, which
includes the protobuf headers necessary to interact with the namenode directly.

The library code within Snakebite doesn't support our desired queries, and so
we use their protobuf headers to write custom code available
[here](https://github.com/mrocklin/distributed/blob/master/distributed/hdfs.py)
(work done by [Ben Zaitlen](https://github.com/quasiben) and
[Martin Durant](https://github.com/martindurant/)).

```python
>>> from distributed import hdfs
>>> blocks = hdfs.get_locations('/data/nyctaxi/', '192.168.50.100', 9000)
>>> blocks
[{'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac15bb90>,
  'hosts': [u'192.168.50.106', u'192.168.50.107', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741844'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac15bf50>,
  'hosts': [u'192.168.50.106', u'192.168.50.107', u'192.168.50.101'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741845'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac15d410>,
  'hosts': [u'192.168.50.107', u'192.168.50.101', u'192.168.50.106'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741846'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac15d848>,
  'hosts': [u'192.168.50.107', u'192.168.50.106', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741847'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac15dc80>,
  'hosts': [u'192.168.50.106', u'192.168.50.105', u'192.168.50.107'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741848'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac16b140>,
  'hosts': [u'192.168.50.107', u'192.168.50.101', u'192.168.50.106'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741849'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac16b578>,
  'hosts': [u'192.168.50.105', u'192.168.50.107', u'192.168.50.106'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741850'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac16b9b0>,
  'hosts': [u'192.168.50.106', u'192.168.50.107', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741851'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac16bde8>,
  'hosts': [u'192.168.50.107', u'192.168.50.106', u'192.168.50.101'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741852'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac1772a8>,
  'hosts': [u'192.168.50.101', u'192.168.50.107', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741853'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac1776e0>,
  'hosts': [u'192.168.50.105', u'192.168.50.107', u'192.168.50.101'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741854'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac177b18>,
  'hosts': [u'192.168.50.101', u'192.168.50.105', u'192.168.50.106'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741855'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac177f50>,
  'hosts': [u'192.168.50.106', u'192.168.50.107', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741856'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac105410>,
  'hosts': [u'192.168.50.107', u'192.168.50.101', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741857'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac105848>,
  'hosts': [u'192.168.50.107', u'192.168.50.106', u'192.168.50.101'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741858'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac105c80>,
  'hosts': [u'192.168.50.106', u'192.168.50.101', u'192.168.50.107'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741859'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac113140>,
  'hosts': [u'192.168.50.106', u'192.168.50.107', u'192.168.50.105'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741860'},
 {'block': <snakebite.protobuf.hdfs_pb2.LocatedBlockProto at 0x7f56ac113578>,
  'hosts': [u'192.168.50.101', u'192.168.50.105', u'192.168.50.106'],
  'path': '/data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741861'}]
```

So we see that our single file, `yellow_tripdata_2014-01.csv`, has been turned
into many small files/blocks, each of which is replicated across three
machines.  We can even go and inspect these blocks.

```
$ ssh hdfs@192.168.50.106
hdfs@compute3:/home/vagrant$ head /data/dfs/dn/current/BP-1962702953-127.0.1.1-1445557266071/current/finalized/subdir0/subdir0/blk_1073741844'},
vendor_id, pickup_datetime, dropoff_datetime, passenger_count, trip_distance, pickup_longitude, pickup_latitude, rate_code, store_and_fwd_flag, dropoff_longitude, dropoff_latitude, payment_type, fare_amount, surcharge, mta_tax, tip_amount, tolls_amount, total_amount

CMT,2014-01-09 20:45:25,2014-01-09 20:52:31,1,0.69999999999999996,-73.994770000000003,40.736828000000003,1,N,-73.982226999999995,40.731789999999997,CRD,6.5,0.5,0.5,1.3999999999999999,0,8.9000000000000004
CMT,2014-01-09 20:46:12,2014-01-09 20:55:12,1,1.3999999999999999,-73.982392000000004,40.773381999999998,1,N,-73.960448999999997,40.763995000000001,CRD,8.5,0.5,0.5,1.8999999999999999,0,11.4
CMT,2014-01-09 20:44:47,2014-01-09 20:59:46,2,2.2999999999999998,-73.988569999999996,40.739406000000002,1,N,-73.986626000000001,40.765217,CRD,11.5,0.5,0.5,1.5,0,14
CMT,2014-01-09 20:44:57,2014-01-09 20:51:40,1,1.7,-73.960212999999996,40.770463999999997,1,N,-73.979862999999995,40.777050000000003,CRD,7.5,0.5,0.5,1.7,0,10.199999999999999
CMT,2014-01-09 20:47:09,2014-01-09 20:53:32,1,0.90000000000000002,-73.995371000000006,40.717247999999998,1,N,-73.984367000000006,40.720523999999997,CRD,6,0.5,0.5,1.75,0,8.75
CMT,2014-01-09 20:45:07,2014-01-09 20:51:01,1,0.90000000000000002,-73.983811000000003,40.749654999999997,1,N,-73.989746999999994,40.756574999999998,CRD,6,0.5,0.5,1.3999999999999999,0,8.4000000000000004
CMT,2014-01-09 20:44:04,2014-01-09 21:05:45,1,3.6000000000000001,-73.984138000000002,40.726317000000002,1,N,-73.962868999999998,40.758443,CRD,16.5,0.5,0.5,5.25,0,22.75
CMT,2014-01-09 20:43:23,2014-01-09 20:52:07,1,2.1000000000000001,-73.979906,40.745849999999997,1,N,-73.959090000000003,40.773639000000003,CRD,9,0.5,0.5,2,0,12
```

Once we have block locations on the host file system we ditch HDFS and just
think about remote hosts that have files on their local file systems.  HDFS has
played its part and can exit the stage.


Data-local tasks with distributed
---------------------------------

We load these blocks with `pandas` and `distributed`.

```python
>>> columns = ['vendor_id', 'pickup_datetime', 'dropoff_datetime',
 'passenger_count', 'trip_distance', 'pickup_longitude', 'pickup_latitude',
 'rate_code', 'store_and_fwd_flag', 'dropoff_longitude', 'dropoff_latitude',
 'payment_type', 'fare_amount', 'surcharge', 'mta_tax', 'tip_amount',
 'tolls_amount', 'total_amount']

>>> from distributed import Executor
>>> executor = Executor('192.168.1.100:8787')
>>> dfs = [executor.submit(pd.read_csv, block['path'], workers=block['hosts'],
...                        columns=columns, skiprows=1)
...        for block in blocks]
```

We use the `workers=` keyword argument to `Executor.submit` to restrict these
jobs so that they can only run on the hosts whose local file systems actually
hold these paths.  Also, because only the first block will have the CSV header
we provide keyword arguments directly to the `pd.read_csv` call.


Or alternatively we've wrapped up both steps into a little convenience function:

```python
>>> from distributed import hdfs
>>> dfs = hdfs.map_blocks(executor, pd.read_csv, '/data/nyctaxi/',
...                       '192.168.50.100', 9000,
...                       columns=columns, skiprows=1)
```


Some simple analysis
--------------------

We now do some simple work, counting all of the passenger counts values.

```python
def sum_series(seq):
    result = seq[0]
    for s in seq[1:]:
        result = result.add(s, fill_value=0)
    return result

>>> counts = executor.map(lambda df: df.passenger_count.value_counts(), dfs)
>>> total = executor.submit(sum_series, counts)
>>> total.result()
0          259
1      9727301
2      1891581
3       566248
4       267540
5       789070
6       540444
7            7
8            5
9           16
208         19
```

Looking at these results we see that as is expected, most rides have a single
passenger.  There are a few oddities like many rides with zero passengers, a
ride with 208 passengers, and an unexpected spike at five passengers.


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
normal tool-set.

That's not to disparage frameworks or elegant streamlined approaches.  If
enough people care about this sort of thing then I may hook up
[dask.dataframe](https://dask.pydata.org/en/latest/dataframe.html) to this in
the near future.

Questions
---------

I'm pretty ignorant when it comes to the JVM HDFS stack.  It'd be great to find
some people out there who are interested by the approach above and knowledgeable
in Hadoop internals that are willing to provide guidance.

*  Are we going down the right path using snakebite/protobufs to interact with
   the namenode?  Should we be doing something else?  `libhdfs` or `webhdfs`
   maybe?
*  What about writing blocks to HDFS?  Is there a non-JVM approach to this?
*  Is there some danger in sidestepping HDFS in this manner?
