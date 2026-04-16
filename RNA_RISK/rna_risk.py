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

        self.lr=0.05

        self.w_ih=[[random.uniform(-1,1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.w_ho=[[random.uniform(-1,1) for _ in range(output_size)] for _ in range(hidden_size)]

        self.b_h=[random.uniform(-1,1) for _ in range(hidden_size)]
        self.b_o=[random.uniform(-1,1) for _ in range(output_size)]


    def forward(self,inputs):

        self.hidden=[]

        for j in range(self.hidden_size):

            s=0
            for i in range(self.input_size):
                s+=inputs[i]*self.w_ih[i][j]

            s+=self.b_h[j]

            self.hidden.append(sigmoid(s))


        self.outputs=[]

        for k in range(self.output_size):

            s=0
            for j in range(self.hidden_size):
                s+=self.hidden[j]*self.w_ho[j][k]

            s+=self.b_o[k]

            self.outputs.append(sigmoid(s))

        return self.outputs


    def train(self,inputs,target):

        outputs=self.forward(inputs)

        output_errors=[target[i]-outputs[i] for i in range(self.output_size)]

        gradients=[output_errors[i]*dsigmoid(outputs[i]) for i in range(self.output_size)]

        for j in range(self.hidden_size):
            for k in range(self.output_size):
                self.w_ho[j][k]+=self.lr*gradients[k]*self.hidden[j]

        for k in range(self.output_size):
            self.b_o[k]+=self.lr*gradients[k]


        hidden_errors=[0]*self.hidden_size

        for j in range(self.hidden_size):

            err=0
            for k in range(self.output_size):
                err+=gradients[k]*self.w_ho[j][k]

            hidden_errors[j]=err


        hidden_grad=[hidden_errors[j]*dsigmoid(self.hidden[j]) for j in range(self.hidden_size)]

        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.w_ih[i][j]+=self.lr*hidden_grad[j]*inputs[i]

        for j in range(self.hidden_size):
            self.b_h[j]+=self.lr*hidden_grad[j]


    def predict(self,inputs):

        outputs=self.forward(inputs)

        return outputs.index(max(outputs))
    
    
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