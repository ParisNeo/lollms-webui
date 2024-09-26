<template>
  <div class="help-view">
    <h1>Bienvenue dans l'aide de Lollms</h1>

    <p>
      **Lollms** (**L**ord **o**f **L**arge **L**anguage and **M**ultimodal **S**ystems), prononcé "lahms", est un outil puissant qui vous permet d'interagir avec une variété de modèles de langage et multimodaux. Il a été créé par **ParisNeo**, un expert en IA et en robotique passionné de programmation depuis son enfance, dans le but de rendre les modèles d'IA accessibles à tous, gratuitement. Son slogan : **"Un outil pour tous les gouverner"**. [1, 2] 
    </p>

    <h2>Composants clés de Lollms</h2>

    <ul>
      <li>
        <b>Liaisons :</b> Essentiellement du code Python, les liaisons sont des modules intermédiaires permettant à Lollms d'interagir avec différents modèles d'IA.  Elles agissent comme des ponts entre l'interface utilisateur de Lollms et les bibliothèques logicielles qui exécutent ces modèles. [3-5]
      </li>
      <li>
        <b>Services :</b> Lollms s'appuie sur des services supplémentaires créés par des développeurs tiers. Ces services, souvent open source, étendent les fonctionnalités de Lollms. Parmi eux, on trouve : [6]
        <ul>
          <li>**Services LLM :**  tels qu'ollama et vllm, dédiés à la génération de texte.</li>
          <li>**Génération d'images :** comme Stable Diffusion, pour créer des images à partir de descriptions textuelles.</li>
          <li>**Synthèse vocale :** comme Xtts, permettant de convertir du texte en parole.</li>
        </ul>
      </li>
      <li>
        <b>Modèles :</b> Au cœur de Lollms se trouvent les modèles de langage. Ces modèles, formés sur d'énormes ensembles de données textuelles, sont capables de : [6-8]
        <ul>
          <li>Générer du texte cohérent et contextuel.</li>
          <li>Traduire des langues avec une précision remarquable.</li>
          <li>Produire différents types de contenu créatif, tels que des poèmes, du code et des scripts.</li>
          <li>Fournir des réponses informatives à vos questions.</li>
        </ul>
        La taille d'un modèle est un facteur déterminant de ses performances : plus le modèle est grand (c'est-à-dire plus il possède de paramètres), plus ses capacités sont généralement avancées. [8, 9]
      </li>
      <li>
        <b>Personnalités :</b> Donnez vie à Lollms grâce aux personnalités. Ces agents virtuels, dotés de caractéristiques et de styles de communication uniques, sont créés par le biais de deux méthodes principales : [10, 11]
        <ul>
          <li>**Conditionnement de texte :** On fournit au modèle des exemples de conversations représentatifs de la personnalité souhaitée, l'entraînant à imiter ce style.</li>
          <li>**Code Python personnalisé :** Des scripts Python permettent de définir des comportements plus complexes et d'intégrer des fonctionnalités spécifiques à une personnalité.</li>
        </ul>
        Avec plus de 250 personnalités disponibles, couvrant des domaines allant de la science à la fiction, vous trouverez forcément celle qui correspond à vos besoins. [10, 12, 13]
      </li>
    </ul>

    <h2>Fonctionnalités de Lollms</h2>

    <p>
      Lollms offre un éventail impressionnant de fonctionnalités :
    </p>

    <ul>
      <li>**Génération de texte :**  Écrivez des histoires, des articles, des poèmes et plus encore.</li>
      <li>**Traduction linguistique :**  Brisez les barrières linguistiques en traduisant du texte dans différentes langues.</li>
      <li>**Écriture créative :** Explorez votre côté artistique en générant des scripts, des poèmes et des paroles de chansons.</li>
      <li>**Réponse aux questions :**  Obtenez des réponses à vos questions en puisant dans les connaissances des modèles de langage.</li>
      <li>**Génération d'images :**  Créez des images uniques à partir de descriptions textuelles.</li>
      <li>**Synthèse vocale :**  Donnez une voix à vos textes grâce à la synthèse vocale.</li>
      <li>**Exécution de code :**  Générez et exécutez du code dans différents langages de programmation.</li>
      <li>**Intégration Web :**  Intégrez Lollms à vos projets web pour des fonctionnalités dynamiques.</li>
      <li>**Et bien plus encore! :**  Lollms est en constante évolution, avec de nouvelles fonctionnalités ajoutées régulièrement.</li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'HelpView',
};
</script>