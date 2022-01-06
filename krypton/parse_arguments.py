# -*- coding: utf-8

import argparse

def parse_argumets(args):
    A = lambda x: args.__dict__[x] if x in args.__dict__ else None
    mode = A('mode')
    output = A('out')
    paired = A('paired')
    fwd = A('r1')
    rev = A('r2')
    transcripts = A('transcripts')
    cds = A('cds')
    bucket_in = A('bucketin')
    bucket_out = A('bucketout')
    hpc2 = A('hpc2')
