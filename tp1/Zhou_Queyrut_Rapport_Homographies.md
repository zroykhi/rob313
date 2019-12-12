TP1 - Estimation d'homographies et reconstruction de panoramas
====

### Auteurs du CR
Zhi Zhou, <zhi.zhou@ensta-paris.fr>
 Simon Queyrut,  <simon.queyrut@ensta-paris.fr>
 
 [@zroykhi](https://github.com/zroykhi) (repo source), [@queyrusi][github] 

[github]: http://github.com/queyrusi

Question 1
------
Nous choisissons comme points d'origine les coins de la mosaïque 
![](https://markdown.data-ensta.fr/uploads/upload_9cd184d4edfcd7f252f93143ed09b7cb.png)

ce qui donne pour la matrice 4x3 :

`PtO = [142.44, 44.894, 1; 356.15, 45.761, 1; 111.86, 253.53, 1;370.59, 260.03, 1]'`

et pour les points de destinations nous choisissons 

`PtD = [120, 20, 1; 320, 20, 1; 120, 320, 1; 320, 320, 1]'`

+ La matrice `A` est celle du problème d'estimation par DLT vu en cours (`w` scale vaut 1)
+ La décomposition SVD est assurée par `[U, S, V] = svd(A, 0)`
+ Nous extrayons la dernière colonne de `V`

Nous appelons `homography2d`  et affichons l'image résultante :
![](https://markdown.data-ensta.fr/uploads/upload_42c82b9894533a34c66915e49567867c.png)

Question 2
------
Dans cette question nous allons coudre ce panorama :
![](https://markdown.data-ensta.fr/uploads/upload_4d7a98bfbc14db9391d0eb1f49d6914e.png)
+ Nous sélectionnons 4 points dans la photo de droite mis dans `PtO` et nous repérons les points correspondants dans la photo du milieu pour les mettre dans`PtD` :


![](https://markdown.data-ensta.fr/uploads/upload_566b801a38b920f2990f88cd472c7151.png)

Cela permet de résoudre le problème d'estimation et trouver `H1`, l'homographie liant ces deux plans avec la question précédente. 
+ Nous faisons un *warp* de la première photo (tout à droite) avec `H1` et une boîte noire de dimensions `[-1500 500 -100 500]` (nous laissons de la place pour la troisième image)
+  *warp* de la deuxième photo (photo du milieu) avec une homographie `H2` (qui est en réalité une identité) avec cette même boîte.  
+ Nous fusionnons ces deux boîtes : `im_fused = max(im1,im2)`
+ Nous augmentons le nombre de points utilisés pour calculer la matrice de transformation. Nous pouvons voir que plus nous utilisons de points, plus l'image est précise après la fusion. Selon **RANSAC**, plus nous utilisons d'échantillons, moins il y a de chance que tous les échantillons soient mauvais, donc le résultat sera plus précis.

4 points  |  8 points | 13 points
:-------------------------:|:-------------------------:|:-------------------------:
![alt text](Panorama_TP/Amst-4-points.jpg)  | ![alt text](Panorama_TP/Amst-8-points.jpg) | ![alt text](Panorama_TP/Amst-13-points.jpg)

+ Nous répétons le processus de couture avec la troisième et dernière image (celle tout à gauche) mais en prenant le panorama obtenu plus ci-dessus et avec une boîte de taille `[-1000 1000 -100 500]`. Enfin, nous utilisons 10 autres points pour fusionner les 3 images ensemble, et le résultat est illustré ci-dessous. 

Fusion de 3 images |
:--------------------------:
![](Panorama_TP/Amst-1-2-3.jpg)

On voit que la qualité de l'image est assez bonne.






