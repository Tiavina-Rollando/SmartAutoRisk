import random
import math
import json


def sigmoid(x):
    return 1/(1+math.exp(-x))


def dsigmoid(y):
    return y*(1-y)


class NeuralNetwork:

    def __init__(self,input_size,hidden_size):

        self.input_size=input_size
        self.hidden_size=hidden_size

        self.lr=0.01

        self.w_ih=[[random.uniform(-1,1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.w_ho=[random.uniform(-1,1) for _ in range(hidden_size)]

        self.b_h=[random.uniform(-1,1) for _ in range(hidden_size)]
        self.b_o=random.uniform(-1,1)


    def forward(self,inputs):

        self.hidden=[]

        for j in range(self.hidden_size):

            s=0
            for i in range(self.input_size):
                s+=inputs[i]*self.w_ih[i][j]

            s+=self.b_h[j]

            self.hidden.append(sigmoid(s))


        s=0

        for j in range(self.hidden_size):
            s+=self.hidden[j]*self.w_ho[j]

        s+=self.b_o

        self.output=s

        return self.output


    def train(self,inputs,target):

        output=self.forward(inputs)

        error=target-output


        for j in range(self.hidden_size):

            grad=error*self.hidden[j]

            self.w_ho[j]+=self.lr*grad

        self.b_o+=self.lr*error


        for j in range(self.hidden_size):

            hidden_error=error*self.w_ho[j]

            hidden_grad=hidden_error*dsigmoid(self.hidden[j])

            for i in range(self.input_size):

                self.w_ih[i][j]+=self.lr*hidden_grad*inputs[i]

            self.b_h[j]+=self.lr*hidden_grad


    def predict(self,inputs):

        return self.forward(inputs)
    

    def save_model(self,filename):

        model={
            "w_ih":self.w_ih,
            "w_ho":self.w_ho,
            "b_h":self.b_h,
            "b_o":self.b_o
        }

        with open(filename,"w") as f:
            json.dump(model,f)


    def load_model(self,filename):

        with open(filename) as f:

            model=json.load(f)

        self.w_ih=model["w_ih"]
        self.w_ho=model["w_ho"]
        self.b_h=model["b_h"]
        self.b_o=model["b_o"]