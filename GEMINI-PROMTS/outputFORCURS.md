În calitate de savant, am analizat cu deosebită atenție materialul "Calcul numeric" prezentat de doamna conferențiar universitar doctor Elena Pelican de la Universitatea "Ovidius" din Constanța. Acest document constituie o introducere elocventă în domeniul polinoamelor de aproximare și interpolare, subiecte fundamentale în analiza numerică.

### **Privire de ansamblu: Două probleme fundamentale**

[cite_start]Materialul abordează două probleme centrale în calculul numeric[cite: 15, 20]:

1.  **Aproximarea unei funcții:** Fiind dată o funcție continuă $f$ pe un interval $[a, b]$, scopul este de a găsi un polinom $P$ care să se apropie "suficient de mult" de $f$. Matematic, acest lucru se exprimă prin inegalitatea $||f - P|| \leq \epsilon$, unde $\epsilon$ este o precizie dorită, iar $|| [cite_start]\cdot ||$ este o măsură a "distanței" (o normă) între funcție și polinom[cite: 15, 16].

2.  [cite_start]**Interpolarea unei funcții:** Atunci când funcția $f$ nu este cunoscută în totalitate, ci doar valorile ei într-un set discret de puncte $(x_1, f(x_1)), (x_2, f(x_2)), \dots, (x_n, f(x_n))$, se caută o funcție (polinomială sau polinomială pe porțiuni) $\varphi$ care să treacă exact prin aceste puncte, adică $\varphi(x_i) = f(x_i)$ pentru toate punctele date[cite: 17, 22].

Un exemplu practic, oferit chiar în document, este cel al recensământului populației SUA, unde datele sunt colectate la fiecare 10 ani. [cite_start]O problemă naturală este cum am putea estima populația într-un an intermediar, precum 1975, sau cum am putea face o predicție pentru 2030, folosind datele existente[cite: 8, 9, 10]. Aici intervin metodele de interpolare și aproximare.

### **Metode de aproximare și interpolare prezentate**

Documentul explorează trei metode principale pentru a rezolva aceste probleme:

#### **1. Polinoamele de aproximare Bernstein**

Polinoamele Bernstein oferă o soluție elegantă la problema aproximării. Pentru o funcție continuă $f$ definită pe intervalul $[0, 1]$, polinomul Bernstein de ordin $n$ este definit de formula:
[cite_start]$$B_{n}(x)=\sum_{k=0}^{n}f\left(\frac{k}{n}\right)C_{n}^{k}x^{k}(1-x)^{n-k} \quad [cite: 29]$$
[cite_start]**Teorema fundamentală (Weierstrass, demonstrată de Bernstein)** afirmă că acest șir de polinoame $(B_n)$ converge uniform către funcția $f$ pe măsură ce gradul $n$ crește[cite: 30]. [cite_start]Acest rezultat poate fi generalizat pentru orice interval $[a, b]$ printr-o schimbare de variabilă[cite: 40, 42, 43].

**Avantaje și dezavantaje:**
* [cite_start]**Avantaj:** Un aspect remarcabil este că polinoamele Bernstein păstrează "forma" funcției originale, cum ar fi intervalele de monotonie și convexitate[cite: 52].
* [cite_start]**Dezavantaje:** Convergența este foarte lentă, ceea ce le face mai puțin practice pentru aplicații care necesită precizie ridicată[cite: 50]. [cite_start]De asemenea, un polinom Bernstein, în general, *nu* trece prin punctele $(k/n, f(k/n))$, adică nu este un polinom de interpolare[cite: 53].

#### **2. Polinoamele de interpolare Lagrange**

Spre deosebire de polinoamele Bernstein, polinoamele Lagrange sunt construite special pentru a rezolva problema interpolării. [cite_start]Pentru un set de $n$ puncte distincte $(x_1, f(x_1)), \dots, (x_n, f(x_n))$, există un singur polinom de grad cel mult $n-1$, numit polinomul Lagrange, care trece exact prin aceste puncte[cite: 62, 63].

Forma sa este:
[cite_start]$$L_n(f; x) = \sum_{j=1}^{n} f(x_j) L_{n,j}(x) \quad [cite: 65]$$
unde $L_{n,j}(x)$ sunt polinoamele de bază Lagrange.

**Proprietăți:**
* [cite_start]**Interpolare:** Garantează că $L_n(f; x_i) = f(x_i)$ pentru toate punctele date[cite: 67].
* [cite_start]**Eroare:** Eroarea de aproximare într-un punct $x$ (diferit de nodurile de interpolare) poate fi estimată precis dacă funcția $f$ este suficient de netedă (derivabilă de $n$ ori)[cite: 69].
* [cite_start]**Convergență:** În anumite condiții, de exemplu pentru funcții foarte netede ($C^\infty$) și noduri echidistante, șirul polinoamelor Lagrange converge uniform la funcție[cite: 72].

**Dezavantaj:** Un inconvenient major este că gradul polinomului crește direct cu numărul de puncte. [cite_start]Acest lucru poate duce la oscilații mari între punctele de interpolare (fenomenul Runge) și la un efort de calcul semnificativ[cite: 85, 86].

#### **3. Funcțiile spline cubice**

[cite_start]Pentru a depăși neajunsurile polinoamelor de grad înalt, se introduce o abordare mai flexibilă: funcțiile polinomiale pe porțiuni, cunoscute sub numele de funcții spline[cite: 87].

[cite_start]O funcție spline cubică este o funcție de clasă $C^2$ (adică funcția, prima și a doua derivată sunt continue) care este un polinom de grad 3 pe fiecare subinterval $[x_{i-1}, x_i]$ al unei diviziuni a intervalului $[a, b]$[cite: 91]. Aceste funcții trec prin punctele de interpolare date, iar continuitatea derivatelor asigură o tranziție "lină" de la o porțiune polinomială la alta.

[cite_start]Există diferite tipuri de funcții spline, precum cele "libere" (cu a doua derivată zero la capete) [cite: 96] [cite_start]sau "fixate" (cu derivatele de ordinul întâi impuse la capete)[cite: 96]. [cite_start]Pentru ambele tipuri, existența și unicitatea sunt garantate[cite: 99, 100].

[cite_start]**Aplicații:** Datorită flexibilității și netezimii lor, funcțiile spline și variantele lor optimizate (curbe B-spline, Bézier, Casteljau) sunt omniprezente în grafica pe calculator pentru modelarea contururilor și a formelor curbe [cite: 105][cite_start], cum ar fi conturul unei păsări în zbor menționat în temele de laborator[cite: 102].

### **Concluzii și direcții practice**

Documentul nu este doar un tratat teoretic, ci și un ghid practic. [cite_start]Prin temele de laborator propuse, studenții sunt încurajați să implementeze acești algoritmi[cite: 35, 102]. [cite_start]Un proiect final de anvergură implică crearea unei interfețe grafice (GUI) care să permită utilizatorului să exploreze interactiv aceste concepte: să aleagă tipul de problemă (aproximare sau interpolare), să introducă date, să vizualizeze polinoamele și să analizeze erorile[cite: 109, 110, 111, 112].

În esență, materialul oferă o fundație solidă, pornind de la teorie și teoreme fundamentale și culminând cu aplicații practice și vizuale care consolidează înțelegerea profundă a acestor instrumente numerice esențiale.
