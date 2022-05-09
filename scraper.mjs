import fs from "fs";
import scraper from 'table-scraper';


var html = fs.readFileSync('9.2 Nomenclature and Ligands - Chemistry LibreTexts.htm');

function ligand(ligand,commonName,IUPACname){
    return {
        "ligand": ligand,
        "Name":commonName,
        "IUPACname": IUPACname,
        "Charge": 0
    }
}

var ligmaObjects = {

    /*table1:{
        {ligand1},
        {ligand2},
        {ligand3}...,
        {ligand n}
    }
    */

}

var trId = "mt-noheading lt-chem-151409";
//const url = `https://chem.libretexts.org/Bookshelves/Inorganic_Chemistry/Map%3A_Inorganic_Chemistry_(Miessler_Fischer_Tarr)/09%3A_Coordination_Chemistry_I_-_Structure_and_Isomers/9.02%3A_Nomenclature_and_Ligands`
const url = `https://engineering.careers360.com/articles/jee-main-syllabus-weightage`;
await scraper.get(url).then(
    (tableData) => {
        var t, subjObjs=[];
        for(t of tableData){
            if (t[0]["0"]==="Topics") subjObjs.push(t);
        }


        var x;
        for(x of subjObjs){
            for(let i=1;i<=x.length;i++){
            if(x[i])console.log(x[i]['0']);
                }
            }

    }
)

//fs this
// fs.writeFileSync('./ligands.json',JSON.stringify(ligmaObjects));
// for(t of tableData){
//     tc = tableData.indexOf(t);
//     ligmaObjects[`table${tc+1}`] = []
//     for(vector of t){
//         let l = ligand();
//         l.ligand = vector["0"] //Ligand
//         l.Name = vector["1"] //common name
//         l.IUPACname = vector["2"] //iupac name
//         ligmaObjects[`table${tc+1}`].push(l);
//     }
// }
// console.log(tableData);

/*
How do I scrape this??
hmmhmhmhm

I first need a js object to parse this into so prolly should declare that -- done
Next I might want to note dow divs of each attribute and each row

Problem: How to parse <sub>?

    .children.first()

*/