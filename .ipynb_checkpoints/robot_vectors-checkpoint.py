import math

def sum_vectors(vectors):
    x_sum = 0
    y_sum = 0
    for length, angle in vectors:
        x_sum += length * math.cos(math.radians(angle))
        y_sum += length * math.sin(math.radians(angle))
    result_length = round(math.sqrt(x_sum**2 + y_sum**2),2)
    result_angle = round(math.degrees(math.atan2(y_sum, x_sum)),2)
    return [result_length, result_angle]

def divide_vector(self,vector, k = 1,rotating = True,degrees = True):
        """"
        input: vectors list(3 vectors);  k - coefficient; rotating vector for length = natural number
        output: vectors [[len,0],[len,120],[len,240]]
        """
        ang_rad = math.radians(vector[1])
        V = vector[0]
        vectors = [None,None,None]
        if degrees:
            vectors[0] = [round(k * V * math.cos(ang_rad),3),0]
            vectors[1] = [round(k * V * math.cos(math.radians(240)-ang_rad),3),240]
            vectors[2] = [round(k * V * math.cos(math.radians(120)-ang_rad),3),120]
        else:
            vectors[0] = round(k * V * math.cos(ang_rad),3)
            vectors[1] = round(k * V * math.cos(math.radians(240)-ang_rad),3)
            vectors[2] = round(k * V * math.cos(math.radians(120)-ang_rad),3)
        
        #print("before rotating:",vectors)
        if rotating:
            for i in range(3):
                if vectors[i][0] < 0:
                    vectors[i][1] += 180
                    vectors[i][1] = vectors[i][1]%360
                    vectors[i][0] = abs(vectors[i][0])
            #print("After rotting",vectors)
        else:
            pass
            #print("NO Rotating")
        return vectors

def rotate_vectors(vectors):
    for i in range(len(vectors)):
        if vectors[i][0]<0:
            vectors[i][0] = abs(vectors[i][0])
            vectors[i][1] += 180

def check_rotation(steps):
    if steps[0]>0 and steps[1]>0 and steps[2] >0:
        rotation_steps = min(steps)
        for i in range(len(steps)):
            steps[i]=steps[i]- rotation_steps
        print("right rotation")
    elif steps[0]<0 and steps[1]<0 and steps[2]<0:
        rotation_steps = max(steps)
        for i in range(len(steps)):
            steps[i]=steps[i]-rotation_steps
        
        print("left rotation")
    else:
        print("no rotations")
        rotation_steps = 0

    #print("steps:",steps)
    return [steps, rotation_steps]

def vector_to_coords(vector):
    x = round(vector[0] * math.cos(math.radians(vector[1])))
    y = round(vector[0] * math.sin(math.radians(vector[1])))
    return x,y

def count_bot_moving(steps,angle,coords):
    """
    input: steps(list), angle robot , координаты робота
    возвращается: координаты конца движения, и угол
    """
    #res = list(list(zip(*aaa))[1]
    vectors = [
    [steps[0],0],
    [steps[1],240],
    [steps[2],120]]
    summed_vector = sum_vectors(vectors)
    a = check_rotation(list(list(zip(*vectors))[0]))
    a[0][0] = [a[0][0],vectors[0][1]]
    a[0][1] = [a[0][1],vectors[1][1]]
    a[0][2] = [a[0][2],vectors[2][1]]
    result = vector_to_coords(summed_vector)

    print("a:",a)
    #print("summed vector:",summed_vector)
    #print("rotation:",a[1])
    #print("res:",result)
    return result, a[1]

if __name__ == "__main__":

    step = [0,10,10]
    print(count_bot_moving(step,0,[0,0]))
