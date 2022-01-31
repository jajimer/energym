import os
from setuptools import setup

with open(os.path.join("sinergym", "version.txt"), "r") as file_handler:
    __version__ = file_handler.read().strip()

with open('requirements.txt') as f:
    reqs = f.read().splitlines()
    
setup(name='sinergym',
      version=__version__,
      license='MIT',
      author='J. Jiménez, J. Gómez, M. Molina, A. Manjavacas, A. Campoy',
      author_email='alejandroac79@gmail.com',
      description='The goal of sinergym is to create an environment following OpenAI Gym interface for wrapping simulation engines for building control using deep reinforcement learning.',
      url='https://github.com/jajimer/sinergym',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Build Tools',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.9'],
      keywords='control reinforcement-learning buildings reinforcement-learning-environments',
      install_requires=reqs,
      include_package_data=True,
      extras_require={
          'extras': [
              'matplotlib',  # visualization
              'stable-baselines3',  # DRL with pytorch
              'mlflow',  # tracking ML experiments
              'tensorflow',
              'tensorboard_plugin_profile',  # Training logger
              'pytest',  # Unit test repository
              'sphinx',  # documentation
              'sphinx-rtd-theme',  # documentation theme
              'google-api-python-client',
              'oauth2client',
              'google-cloud-storage'
          ],
          'test': [
              'pytest'
          ],
          'DRL': [
              'stable-baselines3',
              'mlflow',
              'tensorflow',
              'tensorboard_plugin_profile'
          ],
          'doc': [
              'sphinx',
              'sphinx-rtd-theme'
          ],
          'visualization': [
              'matplotlib',
          ],
          'gcloud': [
              'google-api-python-client',
              'oauth2client',
              'google-cloud-storage'
          ]
      }
    )
