.data

addi $0 $0 1
0_main_1:
addi $t1 0 5
addi $t2 0 10
j cond_2

cond_2:
beq $0 loop_3

loop_3:
j cond_5

cond_5:
beq $0 true_branch_6
j false_branch_7

true_branch_6:
j cond_2

false_branch_7:
j cond_2

