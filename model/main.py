from config import *
from CPmodel import *
import time

if __name__ == '__main__':
    start_time = time.time()

    config = create_config()
    model = CPmodel(config)
    # model.get_data()
    # model.preprocess_data()
    # model.run_model()

    print("run time: ", np.round(time.time() - start_time, 5))
