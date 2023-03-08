from src.business.genre_predictor_pipeline.SliceGenrePredictor import SliceGenrePredictor

if __name__ == '__main__':
    SliceGenrePredictor('dnn/musicDNN.tflearn').run()
