# -*- coding: utf-8 -*-

import tensorflow as tf
import os
import pickle
import numpy as np
from tensorflow.contrib.tensorboard.plugins import projector
import openface
import argparse

def visualize(aligned_dir, out_dir):

    people = np.empty((0, 128))

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with openface.TorchNeuralNet(model='/root/openface/models/openface/nn4.small2.v1.t7') as net:
        with open(os.path.join(out_dir, 'metadata.tsv'), 'wb') as f:
            f.write("Name\tImage\n")
            for img in openface.data.iterImgs(aligned_dir):
                print '%s-%s' % (img.cls, img.name)
                embed = net.forwardPath(img.path)

                people = np.vstack([people, embed])
                f.write("%s\t%s\n" %(img.cls, img.name))

        
    graph = tf.Graph()
    with graph.as_default():
        embedding_var = tf.Variable(tf.random_normal(people.shape), name='faces')

    with tf.Session(graph=graph) as sess:
        tf.global_variables_initializer().run()
        
        sess.run(embedding_var.assign(people))

        config = projector.ProjectorConfig()
        embedding = config.embeddings.add()
        embedding.tensor_name = embedding_var.name
        embedding.metadata_path = 'metadata.tsv'

        summary_writer = tf.summary.FileWriter(out_dir)
        projector.visualize_embeddings(summary_writer, config)

        saver = tf.train.Saver()
        saver.save(sess, os.path.join(out_dir, "model.ckpt"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--aligned_dir',
        type=str,
        help="Path to aligned images directory.",
        default='data/aligned')

    parser.add_argument(
        '--out_dir',
        type=str,
        help="Path to output directory.",
        default='data/visuallize')

    args = parser.parse_args()
    visualize(args.aligned_dir, args.out_dir)
