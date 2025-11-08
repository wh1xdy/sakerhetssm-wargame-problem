INSERT INTO users (id, username) VALUES ('67801911-8d1f-4747-8aa9-a8280222e6df', 'Whitney Smith');
INSERT INTO users (id, username) VALUES ('8dd93d87-78a6-46be-8b52-f396f4730627', 'Billy Bob');

INSERT INTO reviews (
    id,
    user_id,
    review_title,
    book_title,
    isbn,
    rating,
    review,
    is_draft
) VALUES (
    1,
    '67801911-8d1f-4747-8aa9-a8280222e6df',
    'En Färgsprakande Resa Genom Världens Historia',
    'Flags of the World',
    '978-0785818111',
    9,
    'Som en pionjär inom vexillologi och en av de mest erkända flaggforskarna, skulle jag som Whitney Smith beskriva "Flags of the World" av Alistair B. Cook som en imponerande och informativ bok som speglar min egen passion för flaggor, men som också tillför en egen unik dimension till ämnet. Cook har lyckats skapa en resurs som inte bara är en visuell fest utan också en välbehövlig guide till den historiska och kulturella betydelsen av flaggor i världen.

Boken sträcker sig över ett brett spektrum av nationella, regionala och till och med mindre kända flaggor, vilket ger en fantastisk möjlighet för både nybörjare och experter inom vexillologi att fördjupa sig i ämnet. Genom att inkludera detaljerade illustrationer och färgbilder av varje flagga, erbjuder Cook en omfattande och lättförståelig översikt.

Vad som särskiljer "Flags of the World" är Cook"s förmåga att integrera en känsla av historia och betydelse i varje flagga som presenteras. Varje kapitel belyser flaggornas symbolik och deras historiska sammanhang, vilket gör boken till mer än bara en uppslagsbok. Det är en resa genom världens politiska och kulturella landskap, där flaggorna fungerar som speglar av nationell identitet, frihet och kamp.

En av de saker jag särskilt uppskattar är Cooks noggrant sammanställda information om flaggdesignens evolution och de principer som styr dess konstruktion. Som en forskare och förespråkare för vexillologi är jag alltid på jakt efter resurser som främjar förståelsen av flaggornas estetik och funktion, och den här boken levererar på båda fronterna.

Trots bokens styrkor finns det några aspekter som kunde ha utvecklats ytterligare. Det skulle ha varit intressant att se en djupare analys av de mer obskyra flaggorna och deras betydelser, eller till exempel en större fokus på flaggor från icke-nationella enheter såsom städer och organisationer.

Sammanfattningsvis är "Flags of the World" ett utmärkt verk för alla som är intresserade av vexillologi, från de som precis har börjat sitt äventyr i ämnet, till de som har en långvarig passion för flaggornas betydelse och historia. Cook har verkligen lyckats skapa en bok som kombinerar både visuell skönhet och intellektuell stimulans, och som jag varmt kan rekommendera till alla flaggälskare.

Som Whitney Smith skulle jag ge "Flags of the World" av Alistair B. Cook ett betyg på 9 av 10. Boken är en exceptionell resurs som kombinerar visuellt tilltalande bilder med grundlig historisk och symbolisk information om flaggor från hela världen. Den är både informativ och inspirerande för alla som har ett intresse av vexillologi, även om det finns en viss potential för mer djupgående analyser av vissa mer obskyra flaggor.',
    0
);
INSERT INTO comments (review_id, user_id, comment) VALUES (
    1,
    '8dd93d87-78a6-46be-8b52-f396f4730627',
    'Har boken några hobbitar?'
);
INSERT INTO comments (review_id, user_id, comment) VALUES (
    1,
    '67801911-8d1f-4747-8aa9-a8280222e6df',
    'Nej'
);

INSERT INTO reviews (
    id,
    user_id,
    review_title,
    book_title,
    isbn,
    rating,
    review,
    is_draft
) VALUES (
    2,
    '67801911-8d1f-4747-8aa9-a8280222e6df',
    'En Omfattande Resurs för Flagganördar',
    'The Complete Guide to Flags',
    '978-0785806750',
    8,
    'Som Whitney Smith skulle jag beskriva "The Complete Guide to Flags" av Ralph och Linda Kreiger som en ytterst noggrant sammanställd och omfattande bok som ger läsaren en djupare förståelse för flaggornas värld. Kreiger-paret har lyckats skapa en komplett resurs som på ett tydligt och lättillgängligt sätt belyser både de mer välkända och de mindre kända flaggorna, och gör det till en utmärkt källa för både nybörjare och mer erfarna vexillologer.

Boken är indelad på ett sätt som gör det lätt att navigera mellan olika flaggor och deras historiska bakgrund. Med sitt fokus på flaggornas symbolik och designprinciper, ger den en bredare inblick i vad flaggorna representerar, snarare än att bara presentera dem som visuella objekt. Kreiger ger också en övergripande förståelse för hur flaggor har utvecklats och hur de speglar de politiska och sociala förändringar som skett i världen.

En av bokens starkaste sidor är den mängd information den erbjuder om flaggornas färger, mönster och de specifika regler och traditioner som styr designen. För den som vill lära sig om vexillologi på djupet är detta en värdefull källa.

Vad jag skulle kunna önska är kanske mer detaljerad information om vissa flaggors historiska och kulturella kontext, särskilt för de mindre kända eller udda flaggorna. Det skulle också vara intressant att få en djupare analys av flaggornas påverkan på global politik och identitet.

Jag skulle ge "The Complete Guide to Flags" ett betyg på 8 av 10. Det är en mycket välgjord och informativ bok som täcker det mest relevanta inom vexillologi, men den skulle kunna ha gått ännu djupare i vissa aspekter för att ge en fullständig och mer nyanserad bild av flaggornas historia och betydelse.

SSM{Som_Whitney_Smith_skulle_jag_Designa_Fl4ggor_och_Exploatera_D1r3kta_R3f3r3nc3r!}',
    1
);

INSERT INTO reviews (
    id,
    user_id,
    review_title,
    book_title,
    isbn,
    rating,
    review,
    is_draft
) VALUES (
    3,
    '8dd93d87-78a6-46be-8b52-f396f4730627',
    'En Hobbits Äventyr: En Resa Fylld av Vänskap och Fantasi',
    'Hobbiten',
    '978-0261103344',
    10,
    'Det var länge sedan jag läste en bok som fyllde mig med så mycket glädje och äventyr som Hobbiten gör! Den här lilla pärlan från J.R.R. Tolkien tog mig med på en oförglömlig resa genom fantastiska landskap, fyllda med drakar, troll och hobbitar – och vem gillar inte en bra hobbit?

Huvudpersonen Bilbo Bagger är en sådan härlig och oväntad hjälte. Jag menar, vem hade trott att en liten, rund, hårig person skulle vara den som räddar dagen och slåss mot drakar? Det är precis vad som gör honom så charmig. Han börjar sin resa som en oskyldig och tillbakadragen hobbit, men han växer verkligen under resans gång. Att läsa om hans utveckling från en vanlig trädgårdsmästare till en modig äventyrare är en ren fröjd.

Och så alla de andra hobbitarna som hänger med! Låt oss prata om deras namn först och främst – jag menar, är inte Dori, Nori och Ori de mest fantasifulla och roliga namn du någonsin hört? Det känns som att Tolkien satte sitt hjärta och humor i att komma på de mest charmiga, knasiga och ändå passande namn. Balin, Dwalin, Kili och Fili – det är ju som en stor, härlig familj som man bara vill hänga med på varje steg av resan. Jag älskade att läsa om deras vänskap, deras äventyr och hur de alla, på sitt sätt, tillförde något unikt till gruppen.

De små detaljerna och de humoristiska dialogerna gör verkligen boken levande. Jag skrattade flera gånger åt hur alla hobbitarna på något sätt lyckades vara både hjältemodiga och lite blyga samtidigt. Deras sätt att se på världen är så naivt och charmigt, men samtidigt inte utan skärpa och visdom när det verkligen gäller.

Tolkien lyckas också skapa en värld så rik på magi och mystik att det känns som om man nästan kan höra draken Smaugs tunga andetag när man läser. Världen är både farlig och vacker, och för varje kapitel känns det som om vi är närmare att förstå denna märkliga och underbara värld.

Sammanfattningsvis är Hobbiten en bok som inte bara handlar om mod och upptäcktsfärder, utan också om vänskap, samarbete och att finna sin plats i världen – även om man är en liten hobbit. Jag kan inte rekommendera den här boken nog, och jag ser fram emot att läsa om den gång på gång. Och nästa gång någon säger "Vad har du på gång?", kommer jag att tänka på de där härliga hobbitarna och deras stora äventyr!

10 av 10 hobbitfötter',
    0
);
INSERT INTO comments (review_id, user_id, comment) VALUES (
    3,
    '67801911-8d1f-4747-8aa9-a8280222e6df',
    'Inga många flaggor här inte...'
);

