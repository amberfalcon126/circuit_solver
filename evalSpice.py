def nodal_anal(input_list, num, v_count):       #this function makes nodal analysis equation
    #this gives equation for node number "num"
    j=1
    U= unknown_counter(input_list,v_count)
    N=len(U)
    num_nodes = N - v_count
    row =[0 for i in range(N)]
    for i in range(len(input_list)):

        if input_list[i][0][0] == "R":
            if float(input_list[i][-1]) <0 :
                raise ValueError("Malformed circuit file")
            elif float(input_list[i][-1]) ==0:
                input_list[i][-1] = 0.0000000001
            if (input_list[i][1] == ("n" + str(num))) or (input_list[i][2] == ("n" + str(num))):
                row[num - 1] += 1 / (float(input_list[i][3]))
                for j in range(1,N-v_count+1) :
                    if j!= num:
                        if (input_list[i][1] == ("n" + str(j))) or (input_list[i][2] == ("n" + str(j))):
                            row[j-1] = -1 / float(input_list[i][3])
        elif input_list[i][0][0] == "V":
            if input_list[i][3] =="ac":
                raise ValueError("Malformed circuit file")
            if (input_list[i][1] == ("n" + str(num))):
                row[num_nodes] = 1
            elif (input_list[i][2] == ("n" + str(num))):
                row[num_nodes] = -1
            num_nodes += 1
    return row

def v_equation(input_list,num, v_count):        #this function makes the equation for the voltage source
    U = unknown_counter(input_list , v_count)
    N= len(U)
    row =[0 for i in range(N)]
    for i in range(len(input_list)):
        if input_list[i][0] == "V" +str(num):
            if input_list[i][1] in U:
                row[int(input_list[i][1][1])-1] = 1
            if input_list[i][2] in U:
                row[int(input_list[i][2][1]) - 1] = -1

    return row

def b_out(input_list ,v_count):         #this function makes the constants matrix for the input_list given
    U = unknown_counter(input_list,v_count)
    N= len(U)
    row = [0 for i in range(N)]
    nodes = N-v_count
    for i in range(len(input_list)):
        if input_list[i][0][0] =="V":
            row[nodes -1 + int(input_list[i][0][1])] = float(input_list[i][-1])
        elif input_list[i][0][0] == "I":
            if input_list[i][3] =="ac":
                raise ValueError("Malformed circuit file")
            if input_list[i][1] in U:
                row[int(input_list[i][1][1])-1] = -float(input_list[i][-1])
            if input_list[i][2] in U:
                row[int(input_list[i][2][1])-1] = float(input_list[i][-1])
    return row

def gausselim(A, B):       #this function is used for matrix solving
    N = len(A)
    def normalize(A,B,row):
        norm = A[row][row]
        #checks for singular matrix
        if norm == 0:
            raise ValueError('Circuit error: no solution')
        for i in range(len(A[0])): A[row][i] /= norm
        B[row] = B[row]/norm
    for row in range(N):
        normalize(A,B,row)
        for k in range(1, N-row):
            norm = A[row+k][row]
            for j in range(N):
                A[row +k][j] -= norm * A[row][j]
            B[row+k] -= B[row] * norm
    for row in range(N-1, -1, -1):
        for i in range(1,row+1):
            norm1 = A[row-i][row]
            for j in range(N):
                A[row-i][j] -= norm1 * A[row][j]
            B[row-i] -= B[row] * norm1
    return B

def unknown_counter(input_list , v_count):      #this function counts the no. of unique nodes
    unknowns =[]
    for i in range(len(input_list)):
        if input_list[i][1] not in unknowns:
            unknowns.append(input_list[i][1])
        if input_list[i][2] not in unknowns:
            unknowns.append(input_list[i][2])
    unknowns.remove("GND")
    for i in range(v_count):
        unknowns.append("Is"+str(i+1))
    return unknowns

def component_counter(input_list):
    components =[]
    for i in range(len(input_list)):
        if input_list[i][0] in components:
            raise ValueError("Malformed circuit file")
def evalSpice(filename):
    # checks for the file name provided in the directory of the program
    try:
        file1 = open(filename, "r")
        list1 = file1.readlines()
        file1.close()
    except:
        raise FileNotFoundError('Please give the name of a valid SPICE file as input')

    list2 = []
    component_count = {"V": 0, "R": 0, "I": 0}
    for i in range(len(list1)):
        if len(list1[i]) == 0:
            list1[i] = list1[i].split()
    # converting input string to list containing elements only between .circuit and .end
    ckt = False
    for i in range(len(list1)):
        if list1[i] ==".circuit\n":
            ckt = True
        elif list1[i] ==".end\n":
            ckt = False
        if ckt == True:
            list2.append(list1[i])
    if len(list2) ==0:
        raise ValueError('Malformed circuit file')
    else:
        list2.pop(0)
    for i in range(len(list2)):
        list2[i] = list2[i].split()
    #checks for valid elements
    for i in range(len(list2)):
        if list2[i][0][0] not in component_count:
            raise ValueError('Only V, I, R elements are permitted')
        else:
            component_count[list2[i][0][0]] +=1
    # converts the nodes in list2 to a standardized form
    v_count, i_count, switch_v, switch_n =0,0,0,0
    for i in range(len(list2)):
        if list2[i][1].isnumeric():
            list2[i][1] = "n"+ list2[i][1]
            switch_n =1
        if list2[i][2].isnumeric():
            list2[i][2] = "n" + list2[i][2]
            switch_n =1
    # converts the voltage and current sources in list2 to a standardized form
    for i in range(len(list2)):
        if list2[i][0] =="Vsource":
            list2[i][0] = "V" +str(v_count+1)
            v_count+=1
            switch_v =1
        if list2[i][0] == "Isource":
            list2[i][0] = "I" + str(i_count+1)
            i_count += 1
    #removing any comments in the line
    for i in range(len(list2)):
        if "#" in list2[i]:
            index = list2[i].index("#")
            list2[i] = list2[i][:index]

    components =[]
    for i in range(len(list2)):
        if list2[i][0] in components:
            raise ValueError("Malformed circuit file")
        else:
            components.append(list2[i][0])

    v_count = component_count["V"]
    unknowns = unknown_counter(list2 , v_count)
    M= len(unknowns)
    mat =[]
    #calling the nodal_anal and v_equation to make rows of the matrix
    for i in range(1, M-v_count+1):
        mat_n = nodal_anal(list2, i, v_count)
        mat.append(mat_n)
    for i in range(1, v_count+1):
        mat_v = v_equation(list2, i, v_count)
        mat.append(mat_v)
    #making the B matrix
    mat_b = b_out(list2, v_count)
    #using gausselim made for programming 5
    mat_b = gausselim(mat, mat_b)
    #converting the final output in form needed( tuple of two dictionaries
    dict_n ={}
    dict_v ={}
    for i in range(0,M-v_count):
        if switch_n ==1:
            dict_n[str(i+1)] = mat_b[i]
        else:
            dict_n["n"+str(i+1)] =mat_b[i]
    for i in range(1,1+v_count):
        if switch_v == 0:
            dict_v["V"+str(i)] = mat_b[M-v_count+i-1]
        else:
            dict_v["Vsource"] =mat_b[M-v_count+i-1]
    dict_n["GND"] =0
    result =(dict_n, dict_v)

    return (result)

#print(evalSpice("test_2.ckt"))


