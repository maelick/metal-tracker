package net.maelick.metaltracker

import java.util.Date

class Torrent(val name: String, val page: String,
              val metaData: Map[String,String]) {
  override def toString() = {
    String.format("Torrent<%s (%s): %s>", this.name, this.page,
                  this.metaData.toString)
  }

  def toTuple() = {
    (this.name, this.page, this.metaData)
  }

  def toMap() = {
    Map("name" -> this.name, "page" -> this.page, "metaData" -> this.metaData)
  }

  def getNumber(): Int = {
    val re = "/torrents/(\\d+)\\.html".r
    val re(n) = this.page
    n toInt
  }
}
