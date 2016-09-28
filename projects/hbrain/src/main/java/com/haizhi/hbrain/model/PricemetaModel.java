package com.haizhi.hbrain.model;

import com.haizhi.hbrain.util.ToString;
import org.springframework.data.annotation.Id;

import java.util.List;

/**
 * Created by bishop on 28/09/2016.
 */
public class PricemetaModel extends ToString {
    private static final long serialVersionUID = 1L;

    @Id
    private String id;
    private String series;
    private List<String> attrs;
    private String createdTime;
    private String updatedTime;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getSeries() {
        return series;
    }

    public void setSeries(String series) {
        this.series = series;
    }

    public List<String> getAttrs() {
        return attrs;
    }

    public void setAttrs(List<String> attrs) {
        this.attrs = attrs;
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
}
