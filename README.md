# Self-Driving Car Simulator

A 2D simulator where cars learn to drive on their own using a
neural network and a genetic algorithm. No dataset, no hand-written driving rules.

## How it works
- **Sensors:** each car casts 5 rays (-60° to +60°) to measure distance to the road edge
- **Brain:** neural network (5 inputs → 8 hidden → 2 outputs: steering, throttle)
- **Learning:** genetic algorithm with elitism, crossover and mutation
- **Fitness:** checkpoint progress along the track (prevents circling)

## Features
- Live training with generation counter and fitness graph
- Fast mode, save/load best brain, demo mode
- Customizable track

## Run
pip install pygame numpy
python main.py

Controls: F fast, S save, L load, D demo, R restart

## Tech
Python, Pygame, NumPy

## Demo
(https://drive.google.com/file/d/1kyZngNH-no_BYQnPPZlXJvTgwALh1qM_/view?usp=drivesdk)