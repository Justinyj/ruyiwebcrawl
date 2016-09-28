package com.haizhi.hbrain.model;

import com.haizhi.hbrain.util.ToString;
import org.springframework.data.annotation.Id;

import java.util.List;
import java.util.Map;

public class EntitiesModel extends ToString{

	/**
	 * 
	 */
	private static final long serialVersionUID = -8007826315486887330L;

	@Id
	private String id;
	private String gid;
	private String nid;
	private int srank;
	private List<String> tags;
	private List<String> alias;
	private List<Map<String, String>> claims;
	private String createdTime;
	private String updatedTime;
	private String deletedTime;
	private int totalClaim;
	private Map<String, String> source;
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getGid() {
		return gid;
	}
	public void setGid(String gid) {
		this.gid = gid;
	}
	public String getNid() {
		return nid;
	}
	public void setNid(String nid) {
		this.nid = nid;
	}
	public int getSrank() {
		return srank;
	}
	public void setSrank(int srank) {
		this.srank = srank;
	}
	public List<String> getTags() {
		return tags;
	}
	public void setTags(List<String> tags) {
		this.tags = tags;
	}
	public List<String> getAlias() {
		return alias;
	}
	public void setAlias(List<String> alias) {
		this.alias = alias;
	}
	public List<Map<String, String>> getClaims() {
		return claims;
	}
	public void setClaims(List<Map<String, String>> claims) {
		this.claims = claims;
	}
	public String getCreatedTime() {
		return createdTime;
	}
	public void setCreatedTime(String createdTime) {
		this.createdTime = createdTime;
	}
	public String getUpdatedTime() {
		return updatedTime;
	}
	public void setUpdatedTime(String updatedTime) {
		this.updatedTime = updatedTime;
	}
	public String getDeletedTime() {
		return deletedTime;
	}
	public void setDeletedTime(String deletedTime) {
		this.deletedTime = deletedTime;
	}
	public int getTotalClaim() {
		return totalClaim;
	}
	public void setTotalClaim(int totalClaim) {
		this.totalClaim = totalClaim;
	}
	public Map<String, String> getSource() {
		return source;
	}
	public void setSource(Map<String, String> source) {
		this.source = source;
	}
}
