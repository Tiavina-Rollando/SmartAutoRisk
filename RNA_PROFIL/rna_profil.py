import random
import math
import json

def sigmoid(x):
    return 1/(1+math.exp(-x))

def dsigmoid(y):
    return y*(1-y)


class NeuralNetwork:

    def __init__(self,input_size,hidden_size,output_size):

        self.input_size=input_size
        self.hidden_size=hidden_size
        self.output_size=output_size

        self.weights_input_hidden=[[random.uniform(-1,1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.weights_hidden_output=[[random.uniform(-1,1) for _ in range(output_size)] for _ in range(hidden_size)]

        self.bias_hidden=[random.uniform(-1,1) for _ in range(hidden_size)]
        self.bias_output=[random.uniform(-1,1) for _ in range(output_size)]

        self.lr=0.05


    def forward(self,inputs):

        self.hidden=[]

        for j in range(self.hidden_size):

            s=0
            for i in range(self.input_size):
                s+=inputs[i]*self.weights_input_hidden[i][j]

            s+=self.bias_hidden[j]

            self.hidden.append(sigmoid(s))


        self.outputs=[]

        for k in range(self.output_size):

            s=0
            for j in range(self.hidden_size):
                s+=self.hidden[j]*self.weights_hidden_output[j][k]

            s+=self.bias_output[k]

            self.outputs.append(sigmoid(s))

        return self.outputs


    def train(self,inputs,target):

        outputs=self.forward(inputs)

        output_errors=[target[i]-outputs[i] for i in range(self.output_size)]

        gradients=[output_errors[i]*dsigmoid(outputs[i]) for i in range(self.output_size)]

        for j in range(self.hidden_size):
            for k in range(self.output_size):
                self.weights_hidden_output[j][k]+=self.lr*gradients[k]*self.hidden[j]

        for k in range(self.output_size):
            self.bias_output[k]+=self.lr*gradients[k]


        hidden_errors=[0]*self.hidden_size

        for j in range(self.hidden_size):
            err=0
            for k in range(self.output_size):
                err+=gradients[k]*self.weights_hidden_output[j][k]
            hidden_errors[j]=err


        hidden_gradients=[hidden_errors[j]*dsigmoid(self.hidden[j]) for j in range(self.hidden_size)]

        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.weights_input_hidden[i][j]+=self.lr*hidden_gradients[j]*inputs[i]

        for j in range(self.hidden_size):
            self.bias_hidden[j]+=self.lr*hidden_gradients[j]


    def predict(self,inputs):

        outputs=self.forward(inputs)

        return outputs.index(max(outputs))
    

    def save_model(self,filename):

        model={
            "weights_input_hidden":self.weights_input_hidden,
            "weights_hidden_output":self.weights_hidden_output,
            "bias_hidden":self.bias_hidden,
            "bias_output":self.bias_output
        }

        with open(filename,"w") as f:
            json.dump(model,f)

    def load_model(self,filename):

        with open(filename) as f:

            model=json.load(f)

        self.weights_input_hidden=model["weights_input_hidden"]
        self.weights_hidden_output=model["weights_hidden_output"]
        self.bias_hidden=model["bias_hidden"]
        self.bias_output=model["bias_output"]
    