

from config import files
from BusinessLogic.FileOps import *
import matplotlib.pyplot as plt
import pandas as pd

df = GetDataFrameFromJson(files["StateWisePop"])