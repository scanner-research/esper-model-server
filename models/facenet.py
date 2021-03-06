import os
import cv2
import sys
import tensorflow as tf
import numpy as np


class FaceNetEmbed(object):

    def __init__(self, model_dir):
        self.in_size = 160
        self.graph = tf.Graph()
        self.graph.as_default()

        tf_config = tf.ConfigProto(allow_soft_placement=True)
        self.session = tf.Session(config=tf_config)
        self.session.as_default()

        print('Loading face-embeddor model...')
        global facenet
        sys.path.append(model_dir)
        import facenet

        model_data_dir = os.path.join(model_dir, '20170512-110547')
        meta_file, ckpt_file = facenet.get_model_filenames(model_data_dir)
        g = tf.Graph()
        g.as_default()
        saver = tf.train.import_meta_graph(os.path.join(model_data_dir, meta_file))
        saver.restore(self.session, os.path.join(model_data_dir, ckpt_file))

        self.images_placeholder = tf.get_default_graph().get_tensor_by_name('input:0')
        self.embeddings = tf.get_default_graph().get_tensor_by_name('embeddings:0')
        self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name('phase_train:0')
        print('loaded face-embeddor model')

    def embed(self, img):
        [fh, fw] = img.shape[:2]
        if fh == 0 or fw == 0:
            return np.zeros(128, dtype=np.float32).tobytes()
        else:
            img = cv2.resize(img, (self.in_size, self.in_size))
            img = facenet.prewhiten(img)
            embs = self.session.run(
                self.embeddings,
                feed_dict={
                    self.images_placeholder: [img],
                    self.phase_train_placeholder: False
                })
            return embs[0]

    def close(self):
        self.session.close()
