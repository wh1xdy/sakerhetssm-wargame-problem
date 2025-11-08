#include <stdio.h>
#include <string.h>
unsigned int check[] = {169914363, 4063030727, 3037817928, 3691448411, 2139014919, 2450705218, 2064963541, 1515367426, 3244814887, 1023558966, 2456736474, 2747986051, 2575566330, 3717539794, 2294448429, 2270156537, 2523768164, 3831888632, 2600240603, 2985162743, 136908926, 3909501027, 3848493881, 202769529, 1142515344, 2112619257, 1903751617, 1546494057, 881352732};

int main()
{
    char name[30];
	unsigned int out[30];

    printf("Om du är nykter borde detta vara trivialt. Vad är lösenordet? ");
    fgets(name, sizeof(name), stdin);
	name[strcspn(name, "\n")] = 0;
	if (strlen(name)!=sizeof(check)/sizeof(int)) goto lose;
	for(int i=0;i<strlen(name);i++) out[i]=name[i];

	for (int i=0;i<1000000;i++) {
		for (int j=0;j<strlen(name);j++) {
			out[j]=out[j]*1337;
			out[j]^=out[(j+1)%strlen(name)];
		}
	}

	for (int i=0;i<strlen(name);i++){
		if(out[i]!=check[i]){
			goto lose;
		}
	}
	puts("Välkommen!");
	return 0;

	lose:
    puts("Gå och lägg dig");
    return 1;
}