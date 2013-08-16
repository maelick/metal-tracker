package net.maelick.metaltracker

import scala.xml.{Node, NodeSeq}
import java.io.FileWriter
import java.util.Date
import org.yaml.snakeyaml.Yaml

object torrents extends App {
  def parsePage(address: String) = {
    val parserFactory = new org.ccil.cowan.tagsoup.jaxp.SAXFactoryImpl
    val parser = parserFactory.newSAXParser()
    val source = new org.xml.sax.InputSource(address)
    val adapter = new scala.xml.parsing.NoBindingFactoryAdapter
    adapter.loadXML(source, parser)
  }

  def getElement(node: NodeSeq, elementType: String, value: String) = {
    node filter (element => (element \ elementType).text == value)
  }

  def strip(str: String) = {
    str replaceAll ("^\\s|\\s$", "")
  }

  def parseBasicData(node: Node) = {
    val array = node.child.text.split(":", 2).map(strip)
    if (array.length == 2) {
      array.toList.map(strip)
    } else {
      List()
    }
  }

  def getTorrent(node: Node) = {
    val title = getElement(node \\ "img", "@class", "updates") \\ "@title"
    val rawMetaData = getElement(node \\ "ul", "@class", "basic_data") \\ "li"
    val listMetaData = rawMetaData map parseBasicData filter (!_.isEmpty)
    val metaData = listMetaData map (e => (e apply 0, e apply 1)) toMap
    val link = (((node \\ "a") apply 0) \\ "@href").text
    new Torrent(strip(title.text), strip(link), metaData)
  }

  def getNewTorrents(page: String): List[Torrent] = {
    println(String.format("Loading %s", page))
    val xmlTree = parsePage(page)
    val torrents = getElement(xmlTree \\ "div", "@class", "update")
    torrents map getTorrent toList
  }

  def getTorrents(rootPage: String, lastTorrent: Int) = {
    val dateFormat = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    def loop(i: Int, torrents: List[Torrent]): List[Torrent] = {
      val page = rootPage + "/index.php?page=%d".format(i)
      val newTorrents = getNewTorrents(page)
      val maxTorrent = newTorrents.map(_ getNumber).max
      if (maxTorrent >= lastTorrent) {
        loop(i + 1, torrents ++ newTorrents)
      } else {
        torrents ++ newTorrents
      }
    }
    loop(0, List()) reverse
  }

  override def main(args: Array[String]) = {
    val lastTorrent = if (args.length == 0) 71626 else args.apply(0).toInt
    val rootURL = "http://en.metal-tracker.com"
    val torrents = getTorrents(rootURL, lastTorrent)

    def printTorrent(torrent: Torrent) = {
      println(torrent.name)
      if (torrent.metaData contains("Style"))
        println(torrent.metaData apply("Style"))
      if (torrent.metaData contains("Year"))
        println(torrent.metaData apply("Year"))
      if (torrent.metaData contains("Country"))
        println(torrent.metaData apply("Country"))
      if (torrent.metaData contains("File formats"))
        println(torrent.metaData apply("File formats"))
      if (torrent.metaData contains("Size"))
        println(torrent.metaData apply("Size"))
      println(rootURL + torrent.page)
      println()
    }

    torrents foreach printTorrent
  }
}
