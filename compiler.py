import sys
boundedwords = ['program','endprogram','declare','enddeclare','if','then','else','endif','while','endwhile','repeat','endrepeat', 'exit','switch', 'case', 'endswitch','forcase','when', 'endforcase','procedure', 'endprocedure', 'function', 'endfunction', 'call', 'return', 'in', 'inout'
,'and', 'or', 'not', 'true', 'false','input', 'print']

num=0
quad=[]
parameters=[]
quad_id=0
repeat_count=0
return_count=0
exit_count=0
listcall=[]
listdec=[]
allfd=[]

def ASMcode(tempquad,name):
        global scopes
        global mainname
        if(name==mainname):
                sq=mainSQ
        else:
                fname,nest=SearchEntity(name,'func')
                sq=fname.SQ
        for q in quad[sq-1:]:
                file3.write('L_'+str(q[0])+':\n')
                if(q[1]=='jump'):
                        file3.write('\t j L_'+str(q[4])+'\n')
                elif(q[1]=='='):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t beq $t1,$t2,L_'+str(q[4])+'\n')
                elif(q[1]=='<>'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t bne $t1,$t2,L_'+str(q[4])+'\n')
                elif(q[1]=='>'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t bgt $t1,$t2,L_'+str(q[4])+'\n')
                elif(q[1]=='<'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t blt $t1,$t2,L_'+str(q[4])+'\n')
                elif(q[1]=='>='):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t bge $t1,$t2,L_'+str(q[4])+'\n')
                elif(q[1]=='<='):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t ble $t1,$t2,L_'+str(q[4])+'\n')
                elif(q[1]==':='):
                        loadvr(q[2],1)
                        storerv(1,q[4])
                elif(q[1]=='+'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t add $t1,$t1,$t2\n')
                        storerv(1,q[4])
                elif(q[1]=='-'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t sub $t1,$t1,$t2\n')
                        storerv(1,q[4])
                elif(q[1]=='*'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t mul $t1,$t1,$t2\n')
                        storerv(1,q[4])
                elif(q[1]=='/'):
                        loadvr(q[2],1)
                        loadvr(q[3],2)
                        file3.write('\t div $t1,$t1,$t2\n')
                        storerv(1,q[4])
                elif(q[1]=='out'):
                        file3.write('\t li $v0,1\n')
                        loadvr(q[2],1)
                        file3.write('\t addi $a0,$t1,0\n')
                        file3.write('\t syscall\n')
                elif(q[1]=='inp'):
                        file3.write('\t li $v0,5\n')
                        file3.write('\t syscall\n')
                elif(q[1]=='RET'):
                        loadvr(q[4],1)
                        file3.write('\t lw $t0,-8($sp)\n')
                        file3.write('\t sw $t1,($t0)\n')
                elif(q[1]=='par'):
                        if(name==mainname):
                                fl=mainFL
                                file3.write('\t addi $fp,$sp,'+str(mainFL)+'\n')
                                level=0
                        else:
                                fname,fnest=SearchEntity(name,'func')
                                fl=fname.FL
                                level=fnest
                        if(len(parameters)==0):
                                file3.write('\t add $fp,$sp,'+str(fl)+'\n')
                        parameters.append(q)
                        distance=12+4*(len(parameters))
                        if(q[3]=='CV'):
                                loadvr(q[2],0)
                                file3.write('\t sw $t0, -'+str(distance)+'($fp)\n')
                        elif(q[3]=='REF'):
                                qname,qnest=SearchEntity_1(q[2])
                                if(qname.typeof=='var' and qnest==level):
                                        file3.write('\t addi $t0, $sp,-'+str(qname.offset))
                                        file3.write('\t sw $t0, -'+str(distance)+'($fp)\n')
                                if(qname.typeof=='par' and qnest==level and qname.parMode=='CV'):
                                        file3.write('\t addi $t0, $sp,-'+str(qname.offset)+'\n')
                                        file3.write('\t sw $t0, -'+str(distance)+'($fp)\n')
                                if(qname.typeof=='par' and qnest==level and qname.parMode=='REF'):
                                        file3.write('\t lw $t0,-'+str(qname.offfset)+'($sp)\n')
                                        file3.write('\t sw $t0, -'+str(distance)+'($fp)\n')
                                if((qname.typeof=='par' and not(qnest==level) and qname.parMode=='CV') or(qname.typeof=='var')):
                                        gnvlcode(q[2])
                                        file3.write('\t sw $t0, -'+str(distance)+'($fp)\n')
                                if(qname.typeof=='par' and not(qnest==level) and qname.parMode=='REF'):
                                        gnvlcode(q[2])
                                        file3.write('\t lw $t0,($t0)\n')
                                        file3.write('\t sw $t0, -'+str(distance)+'($fp)\n')
                        elif(q[3]=='RET'):
                                qname,qnest=SearchEntity_1(q[2])
                                file3.write('\t addi $t0,$sp,-'+str(qname.offset)+'\n')
                                file3.write('\t sw $t0,-8($fp)\n')                                
                elif(q[1]=='call'):
                        if(name==mainname):
                                fl=mainFL
                                file3.write('\t addi $fp,$sp,'+str(mainFL)+'\n')
                                level=0
                        else:
                                fname,fnest=SearchEntity(name,'func')
                                fl=fname.FL
                                level=fnest
                        qname,qnest=SearchEntity_1(q[2])
                        if(qnest==level):
                                file3.write('\t lw $t0, -4($sp)\n')
                                file3.write('\t sw $t0, -4($fp)\n')
                        else:
                                file3.write('\t sw $sp,-4($fp)\n')
                                file3.write('\t addi $sp,$sp,'+str(fl)+'\n')
                                file3.write('\t jal L_'+str(qname.SQ)+'\n')
                                file3.write('\t addi $sp,$sp,-'+str(fl)+'\n')
                elif(q[1]=='begin_block' and not(name==mainname)):
                        file3.write('\t sw $ra,0($sp)\n')
                elif(q[1]=='begin_block' and name==mainname):
                        file3.write('\t addi $sp,$sp,'+str(mainFL)+'\n')
                        file3.write('\t move $s0,$sp\n')
                elif(q[1]=='end_block'):
                        if (not(name == mainname)):
                                file3.write('\t lw $ra,($sp)\n')
                                file3.write('\t jr $ra\n')
                
		
def EELcode(tempquad):
        for x in tempquad:
                print (x)
                file1.write(str(x))
                file1.write('\n')
        
def Ccode(tempquad):
        c=0
        varlist=[]
        for x in tempquad:
                if(x[1]=='+' or x[1]=='-' or x[1]=='*' or x[1]=='/'):
                        if( x[2].isalpha() and not(x[2] in varlist)):
                                   varlist.append(x[2])
                        if( x[3].isalpha() and not(x[3] in varlist)):
                                   varlist.append(x[3])
                        if( x[4].isalpha() and not(x[4] in varlist)):
                                   varlist.append(x[4])
                if(x[1]==':='):
                        if( x[2].isalpha() and not(x[2] in varlist)):
                                   varlist.append(x[2])
                if(x[1]=='<' or x[1]=='>' or x[1]=='<=' or x[1]=='>=' or x[1]=='<>' or x[1]=='=' ):              
                        if( x[2].isalpha() and not(x[2] in varlist)):
                                   varlist.append(x[2])
                        if( x[3].isalpha() and not(x[3] in varlist)):
                                   varlist.append(x[3])
        file2.write('#include <stdio.h>'+'\n')             
        file2.write('int main()'+'\n')
        file2.write('{'+'\n')
        file2.write('  int ')
        for y in varlist:
                if((len(varlist)-1)==c):
                        file2.write(str(y)+';'+'\n')
                        break
                file2.write(str(y)+',')
                c=c+1
        file2.write('  L_0:'+ '\n')                
        for x in tempquad:
                        if(x[1]=='jump'):
                                file2.write('  goto '+'L_'+ str(x[4])+'; '+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')
                        if(x[1]=='+' or x[1]=='-' or x[1]=='*' or x[1]=='/'):
                                file2.write('  L_'+ str(x[0])+ ': ' + str(x[4]) + '=' + str(x[2]) + str(x[1]) + str(x[3]) + '; '+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n') 
                        if(x[1]=='='):
                                file2.write('  L_'+ str(x[0])+ ': ' + 'if' + '(' + str(x[2]) + '==' + str(x[3]) + ') ' + 'goto ' + 'L_'+ str(x[4])+'; '+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')  
                        if(x[1]==':='):
                                file2.write('  L_'+ str(x[0])+ ': '+ str(x[4]) + '=' + str(x[2])+'; '+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')
                        if(x[1]=='<' or x[1]=='>' or x[1]=='<=' or x[1]=='>='):
                                file2.write('  L_'+ str(x[0])+ ': ' + 'if' + '(' + str(x[2]) + str(x[1]) + str(x[3]) + ') ' + 'goto ' + 'L_'+ str(x[4])+'; '+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')
                        if(x[1]=='<>'):
                                file2.write('  L_'+ str(x[0])+ ': ' + 'if' + '(' + str(x[2]) + '!=' + str(x[3]) + ') ' + 'goto ' + 'L_'+ str(x[4])+'; '+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')
                        if(x[1]=='halt'):
                                file2.write('  L_'+ str(x[0])+ ': ' +'{}'+ '\n')
                        if(x[1]=='out'):
                                file2.write('  L_'+ str(x[0])+ ': ' +'printf'+'('+'"%d/n"'+','+ str(x[2])+')'+';'+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')
                        if(x[1]=='inp'):
                                 file2.write('  L_'+ str(x[0])+ ': ' +'scanf'+'('+'"%d"'+','+ str(x[2])+')'+';'+'//'+'('+ str(x[1])+', '+ str(x[2])+', '+ str(x[3])+', '+ str(x[4])+')' + '\n')
                                
        file2.write('}' + '\n')
######################################################################

def gnvlcode(name):
        global scopes
        
        fname,nest=SearchEntity_1(name)
        if(not(fname.typeof=='func')):
                file3.write('\t lw $t0,-4($sp)\n')
                nest=nest+1
                while(nest<scopes[len(scopes)-1].nestingLevel):
                      file3.write('\t lw $t0,-4($sp)\n')
                      nest+=1
                      
                file3.write('\t addi $t0,$t0,-'+str(fname.offset)+'\n')
        return
        
        
def loadvr(v,r):
        global scopes
        if(v.isdigit()):
                file3.write('\t li $t'+str(r)+','+str(v)+'\n')
                return
        fname,nest=SearchEntity_1(v)
        if(fname.typeof=='var'):
                if(len(scopes)==0):
                        file3.write('\t lw $t'+str(r)+',-'+str(fname.offset)+'($s0)\n')
                if(nest==scopes[len(scopes)-1].nestingLevel):
                        file3.write('\t lw $t'+str(r)+',-'+str(fname.offset)+'($sp)\n')
                if(nest<scopes[len(scopes)-1].nestingLevel):
                        gnvlcode(v)
                        file3.write('\t lw $t'+str(r)+',0($t0)\n')
        elif(fname.typeof=='par'):
                if(fname.parMode=='CV' and nest==scopes[len(scopes)-1].nestingLevel):
                        file3.write('\t lw $t'+str(r)+',-'+str(fname.offset)+'($sp)\n')
                if(fname.parMode=='REF' and nest==scopes[len(scopes)-1].nestingLevel):
                        file3.write('\t lw $t0,-'+str(fname.offset)+'($sp)\n')
                        file3.write('\t lw $t'+str(r)+',0($t0)\n')                        
                if(fname.parMode=='CV' and nest<scopes[len(scopes)-1].nestingLevel):
                        gnvlcode(v)
                        file3.write('\t lw $t'+str(r)+',0($t0)\n')
                if(fname.parMode=='REF' and nest<scopes[len(scopes)-1].nestingLevel):
                        gnvlcode(v)
                        file3.write('\t lw $t0,($t0)\n')
                        file3.write('\t lw $t'+str(r)+',0($t0)\n')
        elif(fname.typeof=='temp'):
                         file3.write('\t lw $t'+str(r)+',-'+str(fname.offset)+'($sp)\n')
        else:
                print('ERROR: Variable is NOT declared:')

def storerv(r,v):
        global scopes
        fname,nest=SearchEntity_1(v)
        if(fname.typeof=='var'):
                if(len(scopes)==0):
                        file3.write('\t sw $t'+str(r)+',-'+str(fname.offset)+'($s0)\n')
                if(nest==scopes[len(scopes)-1].nestingLevel):
                        file3.write('\t sw $t'+str(r)+',-'+str(fname.offset)+'($sp)\n')
                if(nest<scopes[len(scopes)-1].nestingLevel):
                        gnvlcode(fname.name)
                        file3.write('\t sw $t'+str(r)+',($t0)\n')                        
        elif(fname.typeof=='par'):
                if(fname.parMode=='CV' and nest==scopes[len(scopes)-1].nestingLevel):
                        file3.write('\t sw $t'+str(r)+',-'+str(fname.offset)+'($sp)\n')
                if(fname.parMode=='REF' and nest==scopes[len(scopes)-1].nestingLevel):
                        file3.write('\t lw $t0,-'+str(fname.offset)+'($sp)\n')
                        file3.write('\t sw $t'+str(r)+',($t0)\n')                        
                if(fname.parMode=='CV' and nest<scopes[len(scopes)-1].nestingLevel):
                        gnvlcode(fname.name)
                        file3.write('\t sw $t'+str(r)+',($t0)\n')
                if(fname.parMode=='REF' and nest<scopes[len(scopes)-1].nestingLevel):
                        gnvlcode(fname.name)
                        file3.write('\t lw $t0,($t0)\n')
                        file3.write('\t sw $t'+str(r)+',($t0)\n')
        elif(fname.typeof=='temp'):
                         file3.write('\t sw $t'+str(r)+',-'+str(fname.offset)+'($sp)\n')



#######################################################################
scopes=[]
        
class Scope():
        def __init__(self, nestingLevel=0):
                self.Entities=[]
                self.nestingLevel=nestingLevel
                self.offset=12

        def EnterEntity(self,Entity):
                self.Entities.append(Entity)
                
        def get_offset(self):
                temp=self.offset
                self.offset=self.offset+4
                return temp

        def __str__(self):
                return 'NestingLevel: ' + str(self.nestingLevel) +' Offset: '+str(self.offset)

class Entity():

	def  __init__(self,name,typeof):
		self.name=name
		self.typeof=typeof
		self.nextEntity=None

	def __str__(self):
                return ' Typeof: '+str(self.typeof)+' Name: '+str(self.name)

class Variable(Entity):

	def  __init__(self,name,offset=-1):
		super().__init__(name, 'var')
		self.offset=offset

	def __str__(self):
		return super().__str__() + ' Offset: '+str(self.offset)

class Parameter(Entity):

	def  __init__(self,name,parMode,offset=-1):
		super().__init__(name, 'par')
		self.parMode=parMode
		self.offset=offset

	def __str__(self):
                return super().__str__() +  ' Offset: ' + str(self.offset)  +  ' ParMode: ' + str(self.parMode)

class Function(Entity):

	def  __init__(self,name,SQ=-1):
		super().__init__(name, 'func')
		self.FL=-1
		self.SQ=SQ
		self.arglist=[]

	def enterArg(self,arg):
		self.arglist.append(arg)

	def setFL(self, FL):
		self.FL=FL

	def setSQ(self, quad_id):
                self.SQ=quad_id

	def __str__(self):
		return super().__str__() + ', RETV: ' + str(self.typeof) + ', SQ: ' + str(self.SQ) + ', FL: ' + str(self.FL)

class TempVar(Entity):
    def  __init__(self, name, offset=-1):
        super().__init__(name, 'temp')
        self.offset = offset

    def __str__(self):
        return super().__str__() +' Offset: '+ str(self.offset)

	
class Argument():
        def  __init__(self,parMode,Argnext=None):
                self.parMode=parMode
                self.Argnext=Argnext

        def set_next(self, Argnext):
                self.Argnext = Argnext
        
        def __str__(self):
                return ' parMode: '+str(self.parMode)+' Argnext: '+str(self.Argnext)
	

def addNewScope():
        global scopes
        new=Scope((scopes[len(scopes)-1].nestingLevel)+1)
        scopes.append(new)
        
def deleteScope():
        global scopes
        scopes.pop()
        
def addEntity(name,typeof,parMode):
	global scopes
	if(typeof=='var'):
		off=scopes[len(scopes)-1].get_offset()
		new=Variable(name,off)
		scopes[len(scopes)-1].EnterEntity(new)
	if(typeof=='par'):
		off=scopes[len(scopes)-1].get_offset()
		new=Parameter(name,parMode,off)
		scopes[len(scopes)-1].EnterEntity(new)
	if(typeof=='func'):
		new=Function(name,None)
		scopes[len(scopes)-2].EnterEntity(new)
	if(typeof=='temp'):
		off=scopes[len(scopes)-1].get_offset()
		new=TempVar(name,off)
		scopes[len(scopes)-1].EnterEntity(new)
                
	
def addArgument(name,parMode):
         if(parMode=='in'):
                 new=Argument('CV')
                 fname,nest=SearchEntity(name,'func')
                 fname.enterArg(new)
                 
         if(parMode=='inout'):
                new=Argument('REF')
                fname,nest=SearchEntity(name,'func')
                fname.enterArg(new)

                 
def SearchEntity(name,typeof):
        global scopes
        for scope in scopes:
                for entity in scope.Entities:
                    if entity.name == name and entity.typeof == typeof:
                        return entity,scope.nestingLevel
        print('Error:Entity not found')
               
#def SearchEntity_1(name):
#        global scopes
#        for scope in scopes:
#                for entity in scope.Entities:
#                    if entity.name == name:
#                        return entity,scope.nestingLevel
#        print('Error:Entity not found')

def SearchEntity_1(name):
        global scopes
        k=len(scopes)-1
        for i in range(k,-1,-1):
                for entity in scopes[i].Entities:
                        if(entity.name==name):
                                return entity,scopes[i].nestingLevel
        print('Error:Entity not found')
                      
def addFL(name,FL):
        global mainname
        global mainFL
        if( name == mainname):
                mainFL=FL
                return
        fname,nest= SearchEntity(name, 'func')
        fname.setFL(FL)
        
def addSQ(name,quad_id):
        global mainSQ
        global mainname
        if name == mainname:
                mainSQ=quad_id
                return
        fname,nest = SearchEntity(name, 'func')
        fname.setSQ(quad_id)
    

#######################################################################       
def nextquad():
	global quad
	quad_id=len(quad)+1
	return quad_id

def genquad(quad_id,op,x,y,z):
        global qid
        qid=quad_id=nextquad()
        templist=[quad_id,op,x,y,z]
        quad.append(templist)
	
def backpatch(lista,z):
	global quad
	for x in lista:
		for y in quad:
			if x==y[0]:
				y[4]=z
				break
def newTemp():
        global num
        x='T_'
        t=x+str(num)
        num=num+1
        addEntity(t,'temp',None)
        return t

def emptylist():
	emptylist=[]
	return emptylist

def makelist(x):
	l=emptylist()
	l.append(x)
	return l

def mergelist(list1,list2):
	mergedlist=list1+list2
	return mergedlist

########################################
def program():
        global lines
        global tokenboard
        global mainname
        if(tokenboard[1]=='programtk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        mainname=name=tokenboard[0]
                        tokenboard=lektikos_analutis()
                        newScope=Scope()
                        scopes.append(newScope)
                        block(name)
                        if(tokenboard[1]=='endprogramtk'):
                                print('programm ok')
                        else:
                                print('ERROR: <program> The keyword endprogram was expected in line:',(lines+1))
                else:
                        print('ERROR: <program> Program name expected in line:',(lines+1))
        else:
                print('ERROR: <program> The keyword program was expected in line:',(lines+1))


def block(name):
        global lines
        global tokenboard
        global mainname
        global qid
        global quad
        global exit_count
        global repeat_count
        global return_count
        c=0
        declarations()
        subprograms()
        genquad(quad_id,'begin_block',name,' ',' ')
        addSQ(name,qid)
        statements()
        if(name==mainname):
                if(not(return_count==0)):
                        print('ERROR:return in mainprogramm\n')
                genquad(quad_id,'halt',' ',' ',' ')
                addFL(name,scopes[len(scopes)-1].offset)

        genquad(quad_id,'end_block',name,' ',' ')
        for scope in scopes:
                for entity in scope.Entities:
                        for ch in scope.Entities:
                                if(entity.name==ch.name):
                                        c=c+1
                        if(not(c==1)):
                                print('ERROR:Not unique variable,function or procedure name \n')
                                break
                        c=0
        addFL(name,scopes[len(scopes)-1].offset)
        ASMcode(quad,name)
        deleteScope()

def declarations():
        global lines
        global tokenboard
        if(tokenboard[1]=='declaretk'):
                tokenboard=lektikos_analutis()
                varlist()
                if(tokenboard[1]=='enddeclaretk'):
                        tokenboard=lektikos_analutis()  
                else:
                        print('ERROR: <declarations> The keyword enddeclare was expected in line:',(lines+1))
                        
    
def varlist():
        global lines
        global tokenboard
        if(tokenboard[1]=='idtk'):
                addEntity(tokenboard[0],'var',None)
                tokenboard=lektikos_analutis()
                while(tokenboard[1]=='commatk'):
                        tokenboard=lektikos_analutis()
                        if(tokenboard[1]=='idtk'):
                                addEntity(tokenboard[0],'var',None)
                                tokenboard=lektikos_analutis()
                        else:
                                print('ERROR: <varlist>  ID expected in line:',(lines+1))
                                
		
def subprograms():
        global lines
        global tokenboard
        while(tokenboard[1]=='proceduretk' or tokenboard[1]=='functiontk'):
                procorfunc()
		
def procorfunc():
        global lines
        global tokenboard
        global scopes
        global return_count
        global listdec
        global allfd
        if(tokenboard[1]=='proceduretk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        name=tokenboard[0]
                        listdec.append(name)
                        addEntity(name,'func',None)
                        addNewScope()
                        tokenboard=lektikos_analutis()
                        procorfuncbody(name)
                        if(tokenboard[1]=='endproceduretk'):
                                tokenboard=lektikos_analutis()
                                if(not(return_count==0)):
                                        print('ERROR:Return in procedure')
                                return_count=0
                        else:
                                print('ERROR: <procorfunc> The keyword endprocedure was expected in line:',(lines+1))
                else:
                        print('ERROR: <procorfunc> Procedure name expected in line:',(lines+1))
        elif(tokenboard[1]=='functiontk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        name=tokenboard[0]
                        listdec.append(name)
                        addEntity(name,'func',None)
                        addNewScope()
                        tokenboard=lektikos_analutis()
                        procorfuncbody(name)
                        if(tokenboard[1]=='endfunctiontk'):
                                tokenboard=lektikos_analutis()
                                if(return_count==0):
                                        print('ERROR:Not return in function')
                                return_count=0
                        else:
                                print('ERROR: <procorfunc> The keyword endfunction was expected in line:',(lines+1))
                else:
                        print('ERROR: <procorfunc> Function name expected in line:',(lines+1))
        else:
                print('ERROR: <procorfunc> The keywords procedure or function were expected in line:',(lines+1))

def procorfuncbody(name):
        formalpars(name)
        block(name)
	
def formalpars(fname):
        global lines
        global tokenboard
        global listdec
        global allfd
        if(tokenboard[1]=='openbtk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='intk' or tokenboard[1]=='inouttk'):
                        formalparlist(fname)
                        if(tokenboard[1]=='closebtk'):
                                allfd.append(listdec)
                                listdec=[]
                                tokenboard=lektikos_analutis()
                        else:
                                print('ERROR: <formalpars> The symbol ) was expected in line:',(lines+1))
                else:
                        print('ERROR: <formalpars> The keywords in/inout were expected in line:',(lines+1))
        else:
                print('ERROR: <formalpars> The symbol ( was expected in line:',(lines+1))
                

def formalparlist(fname):
        global lines
        global tokenboard
        formalparitem(fname)
        while(tokenboard[1]=='commatk'):
                tokenboard=lektikos_analutis()
                formalparitem(fname)

def formalparitem(fname):
        global lines
        global tokenboard
        global listdec
        if(tokenboard[1]=='intk' or tokenboard[1]=='inouttk'):
                listdec.append(tokenboard[0])
                if(tokenboard[0]=='in'):
                        parMode='CV'
                if(tokenboard[0]=='inout'):
                        parMode='REF'
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        addEntity(tokenboard[0],'par',parMode)
                        addArgument(fname,parMode)
                        tokenboard=lektikos_analutis()
                else:
                        print('ERROR:<formalparitems> Formalparitem id was expected in line:',(lines+1))
        else:
                print('ERROR:<Formalparitem>The keywords in/inout were expected in line:',(lines+1))


def statements():
        global lines
        global tokenboard
        t=[]
        t1=[]
        t=statement()
        while(tokenboard[1]=='questiontk'):
                tokenboard=lektikos_analutis()
                t1=statement()
        return t
                
def statement():
        global lines
        global tokenboard
        t=[]
        if(tokenboard[1]=='idtk'):
                assigment_stat()
                return t
        elif(tokenboard[1]=='iftk'):
                t=if_stat()
                return t
        elif(tokenboard[1]=='whiletk'):
                t=while_stat()
                return t
        elif(tokenboard[1]=='repeattk'):
                repeat_stat()
                return t
        elif(tokenboard[1]=='exittk'):
                t=exit_stat()
                return t
        elif(tokenboard[1]=='switchtk'):
                t=switch_stat()
                return t
        elif(tokenboard[1]=='forcasetk'):
                t=forcase_stat()
        elif(tokenboard[1]=='calltk'):
                 call_stat()
                 return t
        elif(tokenboard[1]=='returntk'):
                return_stat()
        elif(tokenboard[1]=='inputtk'):
                input_stat()
                return t
        elif(tokenboard[1]=='printtk'):
                print_stat()
                return t
       

def assigment_stat():
        global lines
        global tokenboard
        if(tokenboard[1]=='idtk'):
                t=tokenboard[0]
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='assigmenttk'):
                        k=tokenboard[0]
                        tokenboard=lektikos_analutis()
                        eplace=expression()
                        genquad(quad_id,k,eplace,'',t)
                else:
                        print('ERROR:<assigmen_stat> The symbol := was expected in line:',(lines+1))
        else:
                print('ERROR:<assigmen_stat> ID expected in line:',(lines+1))
def if_stat():
        global lines
        global tokenboard
        exitlist=[]
        if(tokenboard[1]=='iftk'):
                tokenboard=lektikos_analutis()
                condtrue,condfalse=condition()
                if(tokenboard[1]=='thentk'):
                        backpatch(condtrue,nextquad())
                        tokenboard=lektikos_analutis()
                        t1=statements()
                        iflist=makelist(nextquad())
                        genquad(quad_id,'jump','','','')
                        backpatch(condfalse,nextquad())
                        t2=else_part()
                        exitlist=mergelist(t1,t2)
                        backpatch(iflist,nextquad())
                        if(tokenboard[1]=='endiftk'):
                                tokenboard=lektikos_analutis()
                        else:
                                print('ERROR:<if_stat> The keyword else was expected in line:',(lines+1))
                else:
                        print('ERROR:<if_stat> The keyword then was expected in line:',(lines+1))
        else:
                print('ERROR:<if_stat> The keyword if was expected in line:',(lines+1))
        return exitlist
                

def else_part():
        global lines
        global tokenboard
        t=[]
        if(tokenboard[1]=='elsetk'):
                tokenboard=lektikos_analutis()
                t=statements()
        return t
                
def repeat_stat():
        global lines
        global tokenboard
        global repeat_count
        global exit_count
        exitlist=[]
        if(tokenboard[1]=='repeattk'):
                repeat_count+=1
                tokenboard=lektikos_analutis()
                sQuad=nextquad()
                t=statements()
                genquad(quad_id,'jump','','',sQuad)
                exitlist=mergelist(exitlist,t)
                if(tokenboard[1]=='endrepeattk'):
                        if(exit_count>0 and repeat_count==0):
                                 print('ERROR:exit without repeat')
                                 exit_count=0
                        repeat_count=0
                        backpatch(exitlist,nextquad())
                        tokenboard=lektikos_analutis()
                else:
                        print('ERROR:<repeat_stat> The keyword endrepeat was expected in line:',(lines+1))
        else:
                print('ERROR:<repeat_stat> The keyword repeat was expected in line:',(lines+1))
                
def exit_stat():
        global lines
        global tokenboard
        global exit_count
        if(tokenboard[1]=='exittk'):
                exit_count=exit_count+1
                t=makelist(nextquad())
                genquad(quad_id,'jump','','','')
                tokenboard=lektikos_analutis()
        else:
                print('ERROR:<exit_stat> The keyword exit was expected in line:',(lines+1))
        return t

def while_stat():
        global lines
        global tokenboard
        if(tokenboard[1]=='whiletk'):
                tokenboard=lektikos_analutis()
                wc=nextquad()
                condtrue,condfalse=condition()
                backpatch(condtrue,nextquad())
                exitlist=statements()
                genquad(quad_id,'jump','','',wc)
                backpatch(condfalse,nextquad())
                if(tokenboard[1]=='endwhiletk'):
                        tokenboard=lektikos_analutis()
                else:
                        print('ERROR:<while_stat> The keyword endwhile was expected in line:',(lines+1))
        else:
                print('ERROR:<whilet_stat> The keyword while was expected in line:',(lines+1))
        return exitlist

def switch_stat():
        global lines
        global tokenboard
        exitrepeat=[]
        if(tokenboard[1]=='switchtk'):
                tokenboard=lektikos_analutis()
                eplace=expression()
                if(tokenboard[1]=='casetk'):
                        tokenboard=lektikos_analutis()
                        eplace1=expression()
                        falsecase=makelist(nextquad())
                        genquad(quad_id,'<>',eplace,eplace1,'')
                        truecase=makelist(nextquad())
                        genquad(quad_id,'=',eplace,eplace1,'')
                        if(tokenboard[1]=='doubledottk'):
                                tokenboard=lektikos_analutis()
                                backpatch(truecase,nextquad())
                                t1=statements()
                                exitlist=makelist(nextquad())
                                genquad(quad_id,'jump','','','')
                                backpatch(falsecase,nextquad())
                                while(tokenboard[1]=='casetk'):
                                        tokenboard=lektikos_analutis()
                                        eplace2=expression()
                                        falsecase1=makelist(nextquad())
                                        genquad(quad_id,'<>',eplace,eplace2,'')
                                        truecase1=makelist(nextquad())
                                        genquad(quad_id,'=',eplace,eplace2,'')
                                        if(tokenboard[1]=='doubledottk'):
                                                tokenboard=lektikos_analutis()
                                                backpatch(truecase1,nextquad())
                                                t2=statements()
                                                exitrepeat=mergelist(t1,t2)
                                                exitlist1=makelist(nextquad())
                                                genquad(quad_id,'jump','','','')
                                                exitlist=mergelist(exitlist,exitlist1)
                                                backpatch(falsecase1,nextquad())
                                if(tokenboard[1]=='endswitchtk'):
                                        backpatch(exitlist,nextquad())
                                        tokenboard=lektikos_analutis()
                                else:
                                        print('ERROR:<switch_stat> The keyword endswitch was expected in line:',(lines+1))
                        else:
                                print('ERROR:<switch_stat> The Symbol : was expected in line:',(lines+1))
                else:
                       print('ERROR:<switch_stat> The keyword case was expected in line:',(lines+1))
        else:
                print('ERROR:<switch_stat> The keyword switch was expected in line:',(lines+1))
        return exitrepeat

def forcase_stat():
        global lines
        global tokenboard
        exitlist=[]
        if(tokenboard[1]=='forcasetk'):
                tokenboard=lektikos_analutis()
                fc=nextquad()
                if(tokenboard[1]=='whentk'):
                        tokenboard=lektikos_analutis()
                        condtrue,condfalse=condition()
                        if(tokenboard[1]=='doubledottk'):
                                tokenboard=lektikos_analutis()
                                backpatch(condtrue,nextquad())
                                t1=statements()
                                genquad(quad_id,'jump','','',fc);
                                backpatch(condfalse,nextquad())
                                while(tokenboard[1]=='whentk'):
                                        tokenboard=lektikos_analutis()
                                        condtrue,condfalse=condition()
                                        if(tokenboard[1]=='doubledottk'):
                                                tokenboard=lektikos_analutis()
                                                backpatch(condtrue,nextquad())
                                                t2=statements()
                                                exitlist=mergelist(t1,t2)
                                                genquad(quad_id,'jump','','',fc);
                                                backpatch(condfalse,nextquad())
                                if(tokenboard[1]=='endforcasetk'):
                                        tokenboard=lektikos_analutis()
                                else:
                                        print('ERROR:<forcase_stat> The keyword endforcase was expected in line:',(lines+1))
                        else:
                                print('ERROR:<forcase_stat> The Symbol : was expected in line:',(lines+1))
                else:
                       print('ERROR:<forcase_stat> The keyword when was expected in line:',(lines+1))
        else:
                print('ERROR:<forcase_stat> The keyword forcase was expected in line:',(lines+1))
        return exitlist
                                
def call_stat():
        global lines
        global tokenboard
        global listcall
        global listdec
        global allfd
        if(tokenboard[1]=='calltk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        x=tokenboard[0]
                        listcall.append(x)
                        tokenboard=lektikos_analutis()
                        actualpars()
                        if listcall not in allfd:
                                print('ERROR:function or procedure not defined')
                        genquad(quad_id,'call',x,'','')
                        listcall=[]
                else:
                        print('ERROR:<call_stat> ID was expected in line:',(lines+1))
        else:
                print('ERROR:<call_stat> The keyword call was expected in line:',(lines+1))



def return_stat():
        global lines
        global tokenboard
        global return_count
        if(tokenboard[1]=='returntk'):
                tokenboard=lektikos_analutis()
                return_count=return_count+1
                eplace=expression()
                genquad(quad_id,'RET','','',eplace)
        else:
                print('ERROR:<return_stat> The keyword return was expected in line:',(lines+1))
                
def print_stat():
        global lines
        global tokenboard
        if(tokenboard[1]=='printtk'):
                tokenboard=lektikos_analutis()
                eplace=expression()
                genquad(quad_id,'out',eplace,'','')
        else:
                print('ERROR:<print_stat> The keyword print was expected in line:',(lines+1))

def input_stat():
        global lines
        global tokenboard
        if(tokenboard[1]=='inputtk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        x=tokenboard[0]
                        tokenboard=lektikos_analutis()
                        genquad(quad_id,'inp',x,'','')
                else:
                        print('ERROR:<input_stat> ID was expected in line:',(lines+1))
        else:
                print('ERROR:<input_stat> The keyword input was expected in line:',(lines+1))

def actualpars():
        global lines
        global tokenboard
        if(tokenboard[1]=='openbtk'):
                tokenboard=lektikos_analutis()
                actualparlist()
                if(tokenboard[1]=='closebtk'):
                        tokenboard=lektikos_analutis()
                else:
                      print('ERROR:<actualpars> The Symbol ) was expected in line:',(lines+1))
        else:
                print('ERROR:<actualpars> The Symbol ) was expected in line:',(lines+1))
                        
def actualparlist():
        global lines
        global tokenboard
        actualparitem()
        while(tokenboard[1]=='commatk'):
                tokenboard=lektikos_analutis()
                actualparitem()
		
def actualparitem():
        global lines
        global tokenboard
        global listcall
        if(tokenboard[1]=='intk'):
                listcall.append(tokenboard[0])
                tokenboard=lektikos_analutis()
                x=expression()
                genquad(quad_id,'par',x,'CV','')
        elif(tokenboard[1]=='inouttk'):
                listcall.append(tokenboard[0])
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='idtk'):
                        genquad(quad_id,'par',tokenboard[0],'REF','')
                        tokenboard=lektikos_analutis()
                else:
                        print('ERROR:<actualparitem> ID was expected in line:',(lines+1))
        else:
                print('ERROR:<actualparitem> The keywords in/out were expected in line:',(lines+1))


def condition():
        global lines
        global tokenboard
       
        condtrue1,condfalse1=boolterm()
        while(tokenboard[1]=='ortk'):
                backpatch(condfalse1,nextquad())
                tokenboard=lektikos_analutis()
                condtrue2,condfalse2=boolterm()
                condtrue1=mergelist(condtrue1,condtrue2)
                condfalse1=condfalse2
        condtrue=condtrue1
        condfalse=condfalse1
        return condtrue,condfalse
def boolterm():
        global lines
        global tokenboard
        btrue1,bfalse1=boolfactor()
        
        while(tokenboard[1]=='andtk'):
                backpatch(btrue1,nextquad())
                tokenboard=lektikos_analutis()
                btrue2,bfalse2=boolfactor()
                bfalse1=mergelist(bfalse1,bfalse2)
                btrue1=btrue2
        btermtrue=btrue1
        btermfalse=bfalse1
        return btermtrue,btermfalse        

def boolfactor():
        global lines
        global tokenboard
        if(tokenboard[1]=='nottk'):
                tokenboard=lektikos_analutis()
                if(tokenboard[1]=='openptk'):
                        tokenboard=lektikos_analutis()
                        Rtrue,Rfalse=condition()
                        if(tokenboard[1]=='closeptk'):
                                tokenboard=lektikos_analutis()
                        else:
                                print('ERROR:<boolfactor> The Symbol ] was expected in line:',(lines+1))
                else:
                        print('ERROR:<boolfactor> The Symbol [ was expected in line:',(lines+1))
        elif(tokenboard[1]=='openptk'):
                tokenboard=lektikos_analutis()
                Rtrue,Rfalse=condition()
                if(tokenboard[1]=='closeptk'):
                        tokenboard=lektikos_analutis()
                else:
                        print('ERROR:<boolfactor> The Symbol ] was expected in line:',(lines+1))
        elif(tokenboard[1]=='truetk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='falsetk'):
                tokenboard=lektikos_analutis()
        else:
                
                eplace1=expression()
                relop=relational_oper()
                eplace2=expression()
                Rtrue=makelist(nextquad())
                genquad(quad_id,relop,eplace1,eplace2,'')
                Rfalse=makelist(nextquad())
                genquad(quad_id,'jump','','','')
        return Rtrue,Rfalse
                
def expression():
        global lines
        global tokenboard
        optional_sign()
        tplace1=term()
        while(tokenboard[1]=='plustk' or tokenboard[1]=='minustk'):
                operation=add_oper()
                tplace2=term()
                w=newTemp()
                genquad(quad_id,operation,tplace1,tplace2,w)
                tplace1=w
        eplace=tplace1
        return eplace

def term():
        global lines
        global tokenboard
        fplace1=factor()
        while(tokenboard[1]=='mulstk' or tokenboard[1]=='divtk'):
                operation=mul_oper()
                fplace2=factor()
                w=newTemp()
                genquad(quad_id,operation,fplace1,fplace2,w)
                fplace1=w
        tplace=fplace1
        return tplace
        
                

def factor():
        global lines
        global tokenboard
        global listcall
        global allfd
        if(tokenboard[1]=='openbtk'):
                tokenboard=lektikos_analutis()
                fplace=expression()
                if(tokenboard[1]=='closebtk'):
                        tokenboard=lektikos_analutis()
                else:
                        print('ERROR:<factor> The Symbol ) was expected in line:',(lines+1))         
        elif(tokenboard[1]=='idtk'):
                fplace=tokenboard[0]
                tokenboard=lektikos_analutis()
                w=idtail(fplace)
                if(w !=''):
                      genquad(quad_id,'call',fplace,'','')
                      if listcall not in allfd:
                              print('ERROR:Function or procedure not exits\n')
                      listcall=[]
                      return w
                
        elif(tokenboard[1]=='consttk'):
                fplace=tokenboard[0]
                tokenboard=lektikos_analutis()
                
        else:
                print('ERROR:<factor> Not ID or Conts or ( founded in line:',(lines+1))
        return fplace

def idtail(fplace):
        global tokenboard
        global listcall
        w=''
        if(tokenboard[1]=='openbtk'):
                listcall.append(fplace)
                actualpars()
                w=newTemp()
                genquad(quad_id,'par',w,'RET','')
        return w
      

def relational_oper():
        global lines
        global tokenboard
        relop=tokenboard[0]
        if(tokenboard[1]=='equalstk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='minequalstk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='maxequalstk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='maxtk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='mintk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='notequalstk'):
                tokenboard=lektikos_analutis()
        else:
                print('ERROR:<relation_oper> == >= <= > < <> expected in line:',(lines+1))
        return relop
def add_oper():
        global lines
        global tokenboard
        operation=tokenboard[0]
        if(tokenboard[1]=='plustk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='minustk'):
                tokenboard=lektikos_analutis()
        else:
                print('ERROR:<add_oper> + or - expected in line:',(lines+1))
        return operation

def mul_oper():
        global lines
        global tokenboard
        op=tokenboard[0]
        if(tokenboard[1]=='mulstk'):
                tokenboard=lektikos_analutis()
        elif(tokenboard[1]=='divtk'):
                tokenboard=lektikos_analutis()
        else:
                print('ERROR:<mul_oper> * or / expected in line:',(lines+1))
        return op

def optional_sign():
        global tokenboard
        if(tokenboard[1]=='plustk' or tokenboard[1]=='minustk'):
                add_oper()

def is_bounded(token):
    global tokenstr 
    if token in boundedwords:
        tokenstr=token+'tk'
    else:
        tokenstr='idtk'
    return

def check_num(token):
    global tokenstr
    global lines
    if((int(token)>32767) or (int(token)<-32767)):
        print('Number out of bounds')
        print('Error  \t in line:',(lines+1))
        exit(1)
    else:
        tokenstr='consttk'
    return

def lektikos_analutis():
    global tokenboard
    global position
    global char
    global lines
    global f
    global state
    global file
    global tokenstr
    global token
    if(position>=len(file)):
        token='eof'
        tokenstr='eoftk'
    while(position<len(file)):
        if(file[position]=='+' and state==0):
            token='+'
            tokenstr='plustk'
            position=position+1
            break
        elif((file[position]=='\t' or file[position].isspace()) and state==0):
            if(file[position]=='\n'):
                    lines=lines+1
            position=position+1
        elif(file[position]=='-' and state==0):
            token='-'
            tokenstr='minustk'
            position=position+1
            break
        elif(file[position]=='*' and state==0):
            token='*'
            tokenstr='mulstk'
            position=position+1
            break
        elif(file[position]=='/' and state==0):
            state=6
            position=position+1
            if(file[position]=='/' and state==6):
                token='//'
                tokenstr='commenttk'
                position=position+1
            elif(file[position]=='*' and state==6):
                state=7
                token='/*'
                tokenstr='commentotk'
                position=position+1
            else:
                token='/'
                state=0
                tokenstr='divtk'
                break
        elif(not(file[position]=='\n') and state==6):
                position=position+1
        elif(not(file[position]=='*') and state==7):
                if(token=='/*' and position==(len(file)-1)):
                        print('ERROR:comments did not close in line:',(lines+1))
                        break
                else:
                        position=position+1	
        elif(file[position]=='*' and state==7):
            position=position+1
            if(file[position]=='/' and state==7):
                state=0
                token='*/'
                tokenstr='commentctk'
                position=position+1
        elif(file[position]=='\n'and state==6):
            lines=lines+1
            state=0
            position=position+1
        elif(file[position]=='=' and state==0):
            token='='
            tokenstr='equalstk'
            position=position+1
            break
        elif(file[position]=='(' and state==0):
            token='('
            tokenstr='openbtk'
            position=position+1
            break
        elif(file[position]==')' and state==0):
            token=')'
            tokenstr='closebtk'
            position=position+1
            break
        elif(file[position]=='[' and state==0):
            token=''
            tokenstr='openptk'
            position=position+1
            break
        elif(file[position]==']' and state==0):
            token=']'
            tokenstr='closeptk'
            position=position+1
            break
        elif(file[position]==',' and state==0):
            token=','
            tokenstr='commatk'
            position=position+1
            break
        elif(file[position]==';' and state==0):
            token=';'
            tokenstr='questiontk'
            position=position+1
            break
        elif(file[position]=='<' and state==0):
            position=position+1
            state=3
            if(file[position]=='>' and state==3):
                token='<>'
                tokenstr='notequalstk'
                position=position+1
                state=0
                break
            elif(file[position]=='=' and state==3):
                token='<='
                tokenstr='minequalstk'
                position=position+1
                state=0
                break
            else:
                token='<'
                tokenstr='mintk'
                state=0
                break
        elif(file[position]=='>' and state==0):
            position=position+1
            state=4
            if(file[position]=='=' and state==4):
                token='>='
                tokenstr='maxequalstk'
                position=position+1
                state=0
                break
            else: 
                token='>'
                tokenstr='maxtk'
                state=0
                break
        elif(file[position]==':' and state==0):
            position=position+1
            state=5
            if(file[position]=='=' and state==5):
                token=':='
                tokenstr='assigmenttk'
                position=position+1
                state=0
                break
            elif(not(file[position]=='=') and state==5):
                token=':'
                tokenstr='doubledottk'
                state=0
                break
        elif(file[position].isalpha() and state==0):
            state=1
            token=file[position]
            position=position+1
        elif((file[position].isalpha() or file[position].isdigit()) and state==1):
                token=token+file[position]
                position=position+1
        elif((not(file[position].isalpha() or file[position].isdigit())) and state==1):
                state=0
                is_bounded(token)
                break
        elif(file[position].isdigit() and state==0):
            state=2
            token=file[position]
            position=position+1
        elif(file[position].isdigit() and state==2):
            token=token+file[position]
            position=position+1
        elif(file[position].isalpha() and state==2):
            print("invalid number")
            exit(1)
        elif(not(file[position].isdigit()and state==2)):
            check_num(token)
            state=0
            break
        else:
            print('Does not belong to the program language in line:',(lines+1))
            print("Error in line:"+(lines+1))
            exit(1)
    return [token, tokenstr]


f=open(sys.argv[1],'r')
file1=open('test.int','w')
file2=open('test.c','w')
file3=open('test.asm','w')
state=0
lines=0
position=0
file=f.read()
tokenboard=lektikos_analutis()
file3.write('\t j L_  \n')
program()
file3.seek(0)
file3.write('\t j L_'+str(mainSQ)+'\n')
EELcode(quad)
Ccode(quad)
file1.close()
file2.close()
file3.close()
