import play.api.libs.json
import scala.io.Source.fromURL
import play.api.libs.json._
import play.api.libs.json.Reads._
import java.util.NoSuchElementException


object test {

  /*def createjson(seq:Seq[JsValue]) : JsObject = {
    myjson = Json.obj()

  }*/

  def main(args: Array[String]): Unit = {
    //val rawJson = fromURL("https://api.travauxlib.com/api/devis-pro/JKusHl8Ba8MABIjdCtLZOe2lxxnUfX").mkString
    try {
      val rawJson = fromURL(args(0)).mkString
      val parseobj = Json.parse(rawJson)
      //println(Json.prettyPrint(test))
      val locations = (parseobj \ "locations").get
      var names = (locations \\ "label")
      var uuids = (locations \\ "uuid")
      names = names :+ (JsString("Autres Prestations"))
      uuids = uuids :+ (null)
      val mymap = uuids.zip(names).toMap
      val lots = (parseobj \ "lots").get
      var i = 0

      var myjson = Json.obj("test" -> Json.toJson("test technique"))
      //var test2 =Json.obj("test"-> myjson("test")).+("test", Json.toJson("value"))
      //test2 = Json.arr().:+(test2).append(Json.toJson("titi"))
      //myjson = myjson.+("test", test2)


      while (i < lots.as[JsArray].value.size) {
        val loc = (lots(i) \\ "locations")
        for (value <- loc) {
          val uuid_lot = (value \\ "uuid")
          if (uuid_lot.isEmpty) {
            try {
              var autrepresta = myjson("Autres prestations")
              autrepresta = Json.arr().:+(autrepresta).append(lots(i))
              myjson = myjson.+("Autres prestations", autrepresta)
            } catch {
              case x: NoSuchElementException => myjson = myjson.+("Autres prestations", lots(i))
            }
          } else {
            for (unit <- uuid_lot) {
              if (mymap(unit) != null) {
                try {
                  var presta = myjson(mymap(unit).toString().replaceAll("^\"+|\"+$", ""))
                  presta = Json.arr().:+(presta).append(lots(i))
                  myjson = myjson.+(mymap(unit).toString().replaceAll("^\"+|\"+$", "") -> presta)
                } catch {
                  case x: NoSuchElementException => myjson = myjson.+(mymap(unit).toString().replaceAll("^\"+|\"+$", "") -> lots(i))
                }
              }
            }
          }
        }
        i += 1
      }
      println(Json.prettyPrint(myjson))
    } catch {
      case x: IndexOutOfBoundsException => println("Please give a valid Url")
    }
  }
}